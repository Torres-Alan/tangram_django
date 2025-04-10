import json
from channels.generic.websocket import AsyncWebsocketConsumer

from estudiantes.models import Estudiante
from sesion_juego.models import Message, SesionJuego
from channels.db import database_sync_to_async

class JuegoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Se ejecuta cuando un cliente intenta conectarse a la sesión """
        # Obtener el código de sesión de la URL
        self.codigo_sesion = self.scope['url_route']['kwargs']['codigo']
        self.sala_grupo = f"juego_{self.codigo_sesion}"

        # Verificar si la sesión está activa
        if not await self.sesion_activa(self.codigo_sesion):
            await self.close()  # Cerrar la conexión si la sesión no está activa
            return

        # Agregar el cliente al grupo de la sala (sesión)
        await self.channel_layer.group_add(self.sala_grupo, self.channel_name)

        # Aceptar la conexión WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        """ Se ejecuta cuando un cliente se desconecta """
        await self.channel_layer.group_discard(self.sala_grupo, self.channel_name)

    async def receive(self, text_data):
        """ Maneja mensajes entrantes (chats o actualizaciones del tangram) """
        data = json.loads(text_data)  # Parsear el JSON recibido
        tipo = data.get('tipo')

        # Manejar según el tipo de mensaje
        if tipo == "chat":
            await self.enviar_mensaje_chat(data)
        elif tipo == "actualizar_tangram":
            await self.actualizar_tangram(data)
        elif tipo == "responder_mensaje":
            await self.responder_mensaje(data)

    @database_sync_to_async
    def guardar_mensaje(self, mensaje,usuario):
        estudiante= Estudiante.objects.get(nickname=usuario)
        #guardar todos los mensajes en el modelo
        mensaje_guardado =  Message.objects.create(
            contenido=mensaje,
            estudiante= estudiante,
        )
        return mensaje_guardado

    async def enviar_mensaje_chat(self, data):
        """ Enviar un mensaje de chat a todos los clientes de la sala """
        mensaje = data["mensaje"]
        usuario = data["usuario"]

        mensaje_guardado=await self.guardar_mensaje(mensaje,usuario,)
        print(f'mensaje guardado: {mensaje_guardado}')
        print(f'id_mensaje: {mensaje_guardado.id}')

        # Enviar el mensaje a todos los miembros del grupo de la sala
        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "chat_message",
                "usuario": usuario,
                "mensaje": mensaje,
                "mensaje_id":mensaje_guardado.id,
            }
        )

    async def actualizar_tangram(self, data):
        """ Compartir el estado del tangram con todos en la sesión """
        estado_tangram = data["estado"]

        # Enviar el estado actualizado del tangram a todos los miembros del grupo
        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "estado_tangram",
                "estado": estado_tangram
            }
        )

    @database_sync_to_async
    def responder_bd(self, respuesta,usuario,mensaje_id):
         # Buscar el mensaje original al que se está respondiendo
        try:
            mensaje_original = Message.objects.get(id=mensaje_id)
        except Message.DoesNotExist:
            return self.send(text_data=json.dumps({
                "error": "Mensaje original no encontrado"
            }))

        estudiante= Estudiante.objects.get(nickname=usuario)
        # Crear el mensaje de respuesta
        mensaje_respuesta =  Message.objects.create(
            estudiante=estudiante,  # Suponiendo que el nombre de usuario es único
            contenido=respuesta,
            mensaje_padre=mensaje_original
        )
    
    
    async def responder_mensaje(self, data):
        """ Manejar la respuesta de un mensaje de chat """
        respuesta=data["respuesta"]
        usuario=data["usuario"]
        mensaje_id=data["mensaje_id"]

        await self.responder_bd(respuesta,usuario,mensaje_id)

        # Enviar la respuesta al grupo
        await self.channel_layer.group_send(
            self.sala_grupo,
            {
                "type": "chat_message",
                "usuario": usuario,
                "mensaje": respuesta,
            }
        )

    
    
    async def sesion_activa(self, codigo):
        """ Verifica si la sesión con el código dado está activa """
        sesion = await SesionJuego.objects.filter(codigo=codigo, activa=True).afirst()
        return sesion is not None  # Retorna True si la sesión existe y está activa

    # Responder con el mensaje de chat
    async def chat_message(self, event):
        """ Enviar mensaje de chat a los clientes de la sala """
        await self.send(text_data=json.dumps({
            "tipo": "chat",
            "usuario": event["usuario"],
            "mensaje": event["mensaje"]
        }))

    # Responder con la actualización del tangram
    async def estado_tangram(self, event):
        """ Enviar actualización del tangram a los clientes de la sala """
        await self.send(text_data=json.dumps({
            "tipo": "actualizar_tangram",
            "estado": event["estado"]
        }))
