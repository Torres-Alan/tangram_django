import json
from channels.generic.websocket import AsyncWebsocketConsumer
from estudiantes.models import Estudiante
from sesion_juego.models import Message, SesionJuego
from channels.db import database_sync_to_async
from django.utils import timezone  
import asyncio  # ← Asegúrate de tener esto al inicio de tu archivo
import time


# Estado en memoria por sesión de juego
estado_sesiones = {}
MAX_CHAT_MENSAJES = 10  # Limitar historial de chat por sesión
# Guarda estadísticas temporales por sesión hasta que se reciba el evidencia_id

estadisticas_temporales = {}


class JuegoConsumer(AsyncWebsocketConsumer):
    # En tu JuegoConsumer.py
    async def connect(self):
        self.codigo_sesion = self.scope['url_route']['kwargs']['codigo']
        self.sala_grupo = f"juego_{self.codigo_sesion}"

        if not await self.sesion_activa(self.codigo_sesion):
            await self.close()
            return

        await self.channel_layer.group_add(self.sala_grupo, self.channel_name)
        await self.accept()
        estado = estado_sesiones.get(self.codigo_sesion, {})
        if "hora_inicio" in estado:
            # Si ya inició, reenviar tiempo
            await self.enviar_tiempo_actividad()

        # 👇 AÑADE esto:
        estado = estado_sesiones.get(self.codigo_sesion, {})
        if "hora_inicio" in estado and "tiempo_total" in estado:
            tiempo_transcurrido = int(timezone.now().timestamp() - estado["hora_inicio"])
            await self.send(text_data=json.dumps({
                "tipo": "tiempo_actividad",
                "tiempo_transcurrido": tiempo_transcurrido,
                "tiempo_total": estado["tiempo_total"]
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.sala_grupo, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        tipo = data.get('tipo')
 
        if tipo == "chat":
            await self.enviar_mensaje_chat(data)
        elif tipo == "actualizar_tangram":
            await self.actualizar_tangram(data)
        elif tipo == "responder_mensaje":
            await self.responder_mensaje(data)
        elif tipo == "bloquear_pieza":
            await self.bloquear_pieza(data)
        elif tipo == "liberar_pieza":
            await self.liberar_pieza(data)
        elif tipo == "usuario_listo":
            await self.usuario_listo(data)
        elif tipo == "usuario_listo_finalizar":
            await self.usuario_listo_finalizar(data)
        elif tipo == "usuario_listo_inicio":
            await self.usuario_listo_inicio(data)
        elif tipo == "reiniciar_sesion":
            await self.reiniciar_sesion(data)
        elif tipo == "solicitar_estado_actual":
            await self.enviar_estado_actual()
        elif tipo == "solicitar_historial_chat":
            await self.enviar_historial_chat()
        elif tipo == "registrar_evidencia":
            await self.registrar_evidencia_id(data)
        elif tipo == "solicitar_tiempo":
            await self.enviar_tiempo_actual()
        elif tipo == "cronometro_terminado":
            await self.cronometro_terminado(data)

    async def enviar_tiempo_actual(self):
        estado = estado_sesiones.get(self.codigo_sesion, {})
        if "hora_inicio" in estado:
            ahora = timezone.now().timestamp()
            tiempo_transcurrido = int(ahora - estado["hora_inicio"])
            tiempo_total = estado.get("tiempo_total", 0)
            segundos_restantes = max(tiempo_total - tiempo_transcurrido, 0)

            await self.send(text_data=json.dumps({
                "tipo": "tiempo_actividad",
                "tiempo_total": tiempo_total,
                "tiempo_transcurrido": tiempo_transcurrido
            })) 

    @database_sync_to_async
    def guardar_estadisticas(self, participacion, evidencia_id):
        from evidencias.models import EstadisticaEvidencia, EvidenciaTangram
        from estudiantes.models import Estudiante

        print("📥 Guardando estadísticas en BD...")

        try:
            evidencia = EvidenciaTangram.objects.get(id=evidencia_id)
        except Exception as e:
            print(f"❌ Error al obtener evidencia: {e}")
            return

        for nickname, stats in participacion.items():
            try:
                estudiante = Estudiante.objects.filter(nickname=nickname).first()
                print(f"👤 Procesando {nickname} → Estudiante: {estudiante}")

                nombre = estudiante.nombre if estudiante else "Desconocido"

                EstadisticaEvidencia.objects.create(
                    evidencia=evidencia,
                    estudiante=estudiante,
                    nombre_estudiante=nombre,
                    nickname_estudiante=nickname,
                    mensajes_enviados=stats.get("mensajes_enviados", 0),
                    respuestas_enviadas=stats.get("respuestas_enviadas", 0),
                    piezas_movidas=stats.get("piezas_movidas", 0),
                )
                print(f"✅ Estadística guardada para {nickname}")
            except Exception as e:
                print(f"❌ Error al guardar estadísticas para {nickname}: {e}")



    @database_sync_to_async
    def guardar_mensaje(self, mensaje, usuario):
        estudiante = Estudiante.objects.get(nickname=usuario)
        mensaje_guardado = Message.objects.create(
            contenido=mensaje,
            estudiante=estudiante,
        )
        return mensaje_guardado

    async def enviar_mensaje_chat(self, data):
        mensaje = data["mensaje"]
        usuario = data["usuario"]

        mensaje_guardado = await self.guardar_mensaje(mensaje, usuario)

        if self.codigo_sesion not in estado_sesiones:
            estado_sesiones[self.codigo_sesion] = {}

        estado = estado_sesiones[self.codigo_sesion]

        # Asegura que exista historial y participacion
        historial = estado.setdefault("chat_historial", [])
        participacion = estado.setdefault("participacion", {})

        # Si es la primera vez del usuario, inicializa sus métricas
        user_stats = participacion.setdefault(usuario, {
            "mensajes_enviados": 0,
            "respuestas_enviadas": 0,
            "piezas_movidas": 0
        })
        user_stats["mensajes_enviados"] += 1

        historial.append({
            "usuario": usuario,
            "mensaje": mensaje,
            "mensaje_id": mensaje_guardado.id
        })

        if len(historial) > MAX_CHAT_MENSAJES:
            historial.pop(0)

        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "chat_message",
                "usuario": usuario,
                "mensaje": mensaje,
                "mensaje_id": mensaje_guardado.id,
            }
        )


    async def actualizar_tangram(self, data):
        estado_tangram = data["estado"]
        usuario = data.get("usuario")  # 🔥 El frontend debe incluir el nickname del usuario que mueve la pieza

        if self.codigo_sesion not in estado_sesiones:
            estado_sesiones[self.codigo_sesion] = {}

        estado = estado_sesiones[self.codigo_sesion]

        estado["pieces"] = estado_tangram.get("pieces", [])
        estado["rotation"] = estado_tangram.get("rotation", {})

        # 🔥 Registrar movimiento de pieza
        if usuario:
            participacion = estado.setdefault("participacion", {})
            user_stats = participacion.setdefault(usuario, {
                "mensajes_enviados": 0,
                "respuestas_enviadas": 0,
                "piezas_movidas": 0
            })
            user_stats["piezas_movidas"] += 1

        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "estado_tangram",
                "estado": estado_tangram
            }
        )


    @database_sync_to_async
    def responder_bd(self, respuesta, usuario, mensaje_id):
        try:
            mensaje_original = Message.objects.get(id=mensaje_id)
        except Message.DoesNotExist:
            return None, None, None

        estudiante = Estudiante.objects.get(nickname=usuario)
        mensaje_respuesta = Message.objects.create(
            estudiante=estudiante,
            contenido=respuesta,
            mensaje_padre=mensaje_original
        )

        return mensaje_respuesta.id, mensaje_original.estudiante.nickname, mensaje_original.contenido

    async def responder_mensaje(self, data):
        respuesta = data["respuesta"]
        usuario = data["usuario"]
        mensaje_id = data["mensaje_id"]

        nuevo_id, original_autor, original_contenido = await self.responder_bd(respuesta, usuario, mensaje_id)

        if not nuevo_id:
            await self.send(text_data=json.dumps({"error": "Mensaje original no encontrado"}))
            return

        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "chat_message",
                "usuario": usuario,
                "mensaje": respuesta,
                "mensaje_id": nuevo_id,
                "mensaje_responde_id": mensaje_id,
                "mensaje_original": {
                    "sender": original_autor,
                    "text": original_contenido,
                }
            }
        )

        if self.codigo_sesion not in estado_sesiones:
            estado_sesiones[self.codigo_sesion] = {}

        estado = estado_sesiones[self.codigo_sesion]

        # Asegura que existan historial y participación
        historial = estado.setdefault("chat_historial", [])
        participacion = estado.setdefault("participacion", {})

        # Inicializa estadísticas si es la primera vez del usuario
        user_stats = participacion.setdefault(usuario, {
            "mensajes_enviados": 0,
            "respuestas_enviadas": 0,
            "piezas_movidas": 0
        })
        user_stats["respuestas_enviadas"] += 1

        historial.append({
            "usuario": usuario,
            "mensaje": respuesta,
            "mensaje_id": nuevo_id,
            "mensaje_responde_id": mensaje_id,
            "mensaje_original": {
                "sender": original_autor,
                "text": original_contenido,
            }
        })

        if len(historial) > MAX_CHAT_MENSAJES:
            historial.pop(0)


    async def sesion_activa(self, codigo):
        sesion = await SesionJuego.objects.filter(codigo=codigo, activa=True).afirst()
        return sesion is not None

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "chat",
            "usuario": event["usuario"],
            "mensaje": event["mensaje"],
            "mensaje_id": event["mensaje_id"],
            "mensaje_responde_id": event.get("mensaje_responde_id"),
            "mensaje_original": event.get("mensaje_original"),
        }))

    async def estado_tangram(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "actualizar_tangram",
            "estado": event["estado"]
        }))

    async def bloquear_pieza(self, data):
        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "pieza_bloqueada",
                "pieza_id": data["pieza_id"],
                "usuario": data["usuario"]
            }
        )

    async def liberar_pieza(self, data):
        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "pieza_liberada",
                "pieza_id": data["pieza_id"]
            }
        )

    async def pieza_bloqueada(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "pieza_bloqueada",
            "pieza_id": event["pieza_id"],
            "usuario": event["usuario"]
        }))

    async def pieza_liberada(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "pieza_liberada",
            "pieza_id": event["pieza_id"]
        }))

    @database_sync_to_async
    def obtener_total_usuarios(self, codigo):
        try:
            sesion = SesionJuego.objects.get(codigo=codigo)
            return Estudiante.objects.filter(equipo=sesion.equipo).count()
        except SesionJuego.DoesNotExist:
            return 0
    @database_sync_to_async
    def obtener_tiempo_total(self, codigo_sesion):
        from actividadesTangram.models import Actividad
        try:
            sesion = SesionJuego.objects.get(codigo=codigo_sesion)
            equipo = sesion.equipo
            salon = equipo.salon
            actividad = Actividad.objects.filter(salon=salon, activo=True).first()

            if not actividad:
                print(f"⚠️ No se encontró actividad activa para el salón {salon}")
                return 600  # fallback

            tiempo_total = (actividad.horas * 3600) + (actividad.minutos * 60) + actividad.segundos
            print(f"⏱️ Tiempo total encontrado para la actividad '{actividad.nombre}': {tiempo_total} segundos")
            return tiempo_total
        except Exception as e:
            print(f"❌ Error al obtener tiempo_total: {e}")
            return 600

    async def usuario_listo(self, data):
        nickname = data.get("usuario")

        if self.codigo_sesion not in estado_sesiones:
            total = await self.obtener_total_usuarios(self.codigo_sesion)
            estado_sesiones[self.codigo_sesion] = {
                "indice": 0,
                "usuarios_listos": set(),
                "total_usuarios": total
            }

        estado = estado_sesiones.setdefault(self.codigo_sesion, {})

        if "usuarios_listos" not in estado:
            estado["usuarios_listos"] = set()
        if "indice" not in estado:
            estado["indice"] = 0
        if "total_usuarios" not in estado:
            estado["total_usuarios"] = await self.obtener_total_usuarios(self.codigo_sesion)

        estado["usuarios_listos"].add(nickname)

        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "enviar_listos",
                "usuarios_listos": list(estado["usuarios_listos"]),
            }
        )

        if len(estado["usuarios_listos"]) >= estado["total_usuarios"]:
            estado["indice"] += 1
            estado["usuarios_listos"] = set()
            estado.pop("pieces", None)
            estado.pop("rotation", None)

            await self.channel_layer.group_send(
                self.sala_grupo,
                {
                    "type": "cambiar_imagen",
                    "nuevo_indice": estado["indice"],
                }
            )


    async def usuario_listo_finalizar(self, data):
        nickname = data.get("usuario")

        if self.codigo_sesion not in estado_sesiones:
            total = await self.obtener_total_usuarios(self.codigo_sesion)
            estado_sesiones[self.codigo_sesion] = {
                "usuarios_listos_finalizar": set(),
                "total_usuarios": total
            }

        estado = estado_sesiones.setdefault(self.codigo_sesion, {})

        if "usuarios_listos_finalizar" not in estado:
            estado["usuarios_listos_finalizar"] = set()
        if "total_usuarios" not in estado:
            estado["total_usuarios"] = await self.obtener_total_usuarios(self.codigo_sesion)

        estado["usuarios_listos_finalizar"].add(nickname)

        print(f"✅ [{self.codigo_sesion}] {nickname} está listo para finalizar")
        print(f"✅ Listos hasta ahora: {estado['usuarios_listos_finalizar']}/{estado['total_usuarios']}")

        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "enviar_listos_finalizar",
                "usuarios_listos_finalizar": list(estado["usuarios_listos_finalizar"]),
            }
        )

        if len(estado["usuarios_listos_finalizar"]) >= estado["total_usuarios"]:
            participacion = estado.get("participacion", {})
            estadisticas_temporales[self.codigo_sesion] = participacion

            # ✅ Avisa al último para ejecutar handleFinalizar
            await self.send(text_data=json.dumps({
                "tipo": "todos_finalizar",
                "ultimo_en_finalizar": nickname
            }))

            # ❌ NO mandes salir todavía, espera a que llegue registrar_evidencia


    async def enviar_listos(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "usuario_listo",
            "usuarios_listos": event["usuarios_listos"]
        }))

    async def enviar_listos_finalizar(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "usuarios_listos_finalizar",
            "usuarios_listos_finalizar": event["usuarios_listos_finalizar"]
        }))


    async def usuario_listo_inicio(self, data):
        nickname = data.get("usuario")

        if self.codigo_sesion not in estado_sesiones:
            total = await self.obtener_total_usuarios(self.codigo_sesion)
            estado_sesiones[self.codigo_sesion] = {
                "usuarios_listos_inicio": set(),
                "total_usuarios": total
            }

        estado = estado_sesiones.setdefault(self.codigo_sesion, {})

        if "usuarios_listos_inicio" not in estado:
            estado["usuarios_listos_inicio"] = set()
        if "total_usuarios" not in estado:
            estado["total_usuarios"] = await self.obtener_total_usuarios(self.codigo_sesion)

        estado["usuarios_listos_inicio"].add(nickname)

        # 🔥 Notifica a todos quiénes ya le dieron a "Estoy listo"
        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "enviar_listos_inicio",
                "usuarios_listos_inicio": list(estado["usuarios_listos_inicio"]),
            }
        )

        # 🔥 Si todos ya dieron click, empieza el juego
        if len(estado["usuarios_listos_inicio"]) >= estado["total_usuarios"]:
            from django.utils.timezone import now
            # Solo si no se ha guardado antes
            if "hora_inicio" not in estado:
                estado["hora_inicio"] = now().timestamp()

                # 🔥 AÑADE ESTO: Define el tiempo total de la actividad
                estado["tiempo_total"] = await self.obtener_tiempo_total(self.codigo_sesion)

            await self.channel_layer.group_send(
                self.sala_grupo,
                {
                    "type": "todos_listos_inicio"
                }
            )

    
    async def enviar_listos_inicio(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "usuarios_listos_inicio",
            "usuarios_listos_inicio": event["usuarios_listos_inicio"]
        }))

    async def todos_listos_inicio(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "todos_listos_inicio"
        }))


    async def todos_finalizar(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "todos_finalizar"
        }))

    async def enviar_tiempo_actividad(self, event=None):
        estado = estado_sesiones.get(self.codigo_sesion, {})

        if "hora_inicio" not in estado:
            return

        tiempo_transcurrido = int(timezone.now().timestamp() - estado["hora_inicio"])
        tiempo_total = estado.get("tiempo_total", 3600)  # 👈 aquí debería estar el tiempo definido por el profe

        await self.send(text_data=json.dumps({
            "tipo": "tiempo_actividad",
            "tiempo_transcurrido": tiempo_transcurrido,
            "tiempo_total": tiempo_total  # 👈 ahora sí lo mandas
        }))


    async def cambiar_imagen(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "cambiar_imagen",
            "nuevo_indice": event["nuevo_indice"]
        }))

    async def reiniciar_sesion(self, event):
        codigo = self.codigo_sesion

        if codigo not in estado_sesiones:
            estado_sesiones[codigo] = {}

        estado_sesiones[codigo]["indice"] = 0
        estado_sesiones[codigo]["usuarios_listos"] = set()
        estado_sesiones[codigo]["total_usuarios"] = await self.obtener_total_usuarios(codigo)

        if "pieces" in estado_sesiones[codigo]:
            estado_sesiones[codigo].pop("pieces")
        if "rotation" in estado_sesiones[codigo]:
            estado_sesiones[codigo].pop("rotation")
        if "usuarios_listos_finalizar" in estado_sesiones[codigo]:
            estado_sesiones[codigo].pop("usuarios_listos_finalizar")

        await self.send(text_data=json.dumps({
            "tipo": "reiniciar_sesion",
            "mensaje": "Sesión reiniciada correctamente."
        }))

    async def enviar_estado_actual(self):
        estado = estado_sesiones.get(self.codigo_sesion, {})

        if "hora_inicio" in estado:
            tiempo_transcurrido = timezone.now().timestamp() - estado["hora_inicio"]
            total_segundos = (self.scope["session_tiempo_segundos"]) if hasattr(self.scope, "session_tiempo_segundos") else 3600  # fallback de 1hr
            segundos_restantes = max(0, int(total_segundos - tiempo_transcurrido))
        else:
            segundos_restantes = None

        await self.send(text_data=json.dumps({
            "tipo": "estado_actual",
            "estado": {
                "pieces": estado.get("pieces", []),
                "rotation": estado.get("rotation", {}),
                "indice": estado.get("indice", 0),
                "usuarios_listos": list(estado.get("usuarios_listos", set())),
                "usuarios_listos_finalizar": list(estado.get("usuarios_listos_finalizar", set())),
            }
        }))

    async def enviar_historial_chat(self):
        estado = estado_sesiones.get(self.codigo_sesion, {})
        historial = estado.get("chat_historial", [])

        await self.send(text_data=json.dumps({
            "tipo": "historial_chat",
            "mensajes": historial
        }))

    async def registrar_evidencia_id(self, data):
        evidencia_id = data.get("evidencia_id")
        nickname = data.get("nickname")

        print(f"📩 RECIBIDO registrar_evidencia: evidencia_id={evidencia_id}, nickname={nickname}")

        if self.codigo_sesion not in estado_sesiones:
            print(f"⚠️ No hay estado para la sesión {self.codigo_sesion}")
            await self.send(text_data=json.dumps({
                "tipo": "registro_estadisticas_error",
                "error": f"No hay estado para la sesión {self.codigo_sesion}"
            }))
            return

        estado_sesiones[self.codigo_sesion]["evidencia_id"] = evidencia_id
        print(f"✅ Evidencia {evidencia_id} registrada en estado para sesión {self.codigo_sesion}")

        participacion = estado_sesiones[self.codigo_sesion].get("participacion", {})
        print(f"📊 Datos de participación: {participacion}")

        if evidencia_id and self.codigo_sesion in estadisticas_temporales:
            try:
                await self.guardar_estadisticas_por_evidencia_id(
                    evidencia_id,
                    estadisticas_temporales[self.codigo_sesion]
                )
                print(f"✅ Estadísticas guardadas para evidencia {evidencia_id}")

                # 🔔 Notificar éxito solo al que envió
                await self.send(text_data=json.dumps({
                    "tipo": "registro_estadisticas_ok",
                    "evidencia_id": evidencia_id
                }))

                # 🔁 Notificar a todos para salir
                await self.channel_layer.group_send(
                    self.sala_grupo,
                    {
                        "type": "forzar_salida"
                    }
                )

            except Exception as e:
                print(f"❌ Error guardando estadísticas: {str(e)}")

                # ❌ Notificar error al frontend
                await self.send(text_data=json.dumps({
                    "tipo": "registro_estadisticas_error",
                    "error": str(e)
                }))

            del estadisticas_temporales[self.codigo_sesion]

        # ✅ Siempre se hace al final
        estado_sesiones.pop(self.codigo_sesion, None)




    @database_sync_to_async
    def guardar_estadisticas_por_evidencia_id(self, evidencia_id, datos_participacion):
        from evidencias.models import EstadisticaEvidencia, Estudiante
        from django.db import transaction

        with transaction.atomic():
            for nickname, valores in datos_participacion.items():
                estudiante = Estudiante.objects.filter(nickname=nickname).first()
                if estudiante:
                    EstadisticaEvidencia.objects.create(
                        evidencia_id=evidencia_id,
                        estudiante=estudiante,
                        nombre_estudiante=estudiante.nombre,
                        nickname_estudiante=nickname,
                        mensajes_enviados=valores.get("mensajes_enviados", 0),
                        respuestas_enviadas=valores.get("respuestas_enviadas", 0),
                        piezas_movidas=valores.get("piezas_movidas", 0),
                    )

    async def forzar_salida(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "salir_al_login"
        }))
        
    async def cronometro_terminado(self, data):
        estado = estado_sesiones.get(self.codigo_sesion, {})

        if estado.get("tiempo_finalizado"):
            print("⛔ Ya se había enviado finalizar_por_tiempo.")
            return

        estado["tiempo_finalizado"] = True

        # ❗ Notificar a todos que deben finalizar manualmente
        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "tiempo_agotado"
            }
        )

    async def tiempo_agotado(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "tiempo_agotado"
        }))
        
    async def finalizar_por_tiempo(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "finalizar_por_tiempo",
            "nickname": event["nickname"]
        }))