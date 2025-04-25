import json
from channels.generic.websocket import AsyncWebsocketConsumer
from estudiantes.models import Estudiante
from sesion_juego.models import Message, SesionJuego
from channels.db import database_sync_to_async

# Estado en memoria por sesión de juego
estado_sesiones = {}

class JuegoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.codigo_sesion = self.scope['url_route']['kwargs']['codigo']
        self.sala_grupo = f"juego_{self.codigo_sesion}"

        if not await self.sesion_activa(self.codigo_sesion):
            await self.close()
            return

        await self.channel_layer.group_add(self.sala_grupo, self.channel_name)
        await self.accept()

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
        elif tipo == "reiniciar_sesion":  
            await self.reiniciar_sesion(data)

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
            await self.send(text_data=json.dumps({
                "error": "Mensaje original no encontrado"
            }))
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

    # ------------------------------
    # NUEVA LÓGICA: Turnos / Imagen
    # ------------------------------

    @database_sync_to_async
    def obtener_total_usuarios(self, codigo):
        try:
            sesion = SesionJuego.objects.get(codigo=codigo)
            return Estudiante.objects.filter(equipo=sesion.equipo).count()
        except SesionJuego.DoesNotExist:
            return 0

    async def usuario_listo(self, data):
        nickname = data.get("usuario")

        if self.codigo_sesion not in estado_sesiones:
            total = await self.obtener_total_usuarios(self.codigo_sesion)
            estado_sesiones[self.codigo_sesion] = {
                "indice": 0,
                "usuarios_listos": set(),
                "total_usuarios": total
            }

        estado = estado_sesiones[self.codigo_sesion]
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

            await self.channel_layer.group_send(
                self.sala_grupo,
                {
                    "type": "cambiar_imagen",
                    "nuevo_indice": estado["indice"],
                }
            )

    async def enviar_listos(self, event):
        await self.send(text_data=json.dumps({
            "tipo": "usuario_listo",
            "usuarios_listos": event["usuarios_listos"]
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
        estado_sesiones[codigo]["total_usuarios"] = await self.obtener_total_usuarios(codigo)  # 🔥 Agregado esto
        
        print(f"🌀 Sesión reiniciada en servidor para: {codigo}")

        await self.send(text_data=json.dumps({
            "tipo": "reiniciar_sesion",
            "mensaje": "Sesión reiniciada correctamente."
        }))



    