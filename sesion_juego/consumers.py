# sesion_juego/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extraer el 'room_name' de la URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Unirse a la sala de chat
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Salir de la sala de chat
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Recibir un mensaje y enviarlo a todos los usuarios en el grupo
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Enviar el mensaje a todos los miembros del grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # Enviar el mensaje al WebSocket
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
