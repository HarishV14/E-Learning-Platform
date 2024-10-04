import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone
import uuid

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = 'chat_%s' % self.id
        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept connection
        self.accept()
        
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json['type'] == 'message':
            self.handle_message(text_data_json['message'])
        elif text_data_json['type'] == 'delete':
            self.handle_delete(text_data_json['message_id'])

    def handle_message(self, message):
        now = timezone.now()
        message_id = str(uuid.uuid4())  # Generate a new UUID for the message
        
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                'type': 'chat_message',
                'message': message,
                'message_id': message_id,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )

    def handle_delete(self, message_id):
        # Send delete message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                'type': 'chat_delete',
                'message_id': message_id,
            }
        )
        
    def chat_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

    def chat_delete(self, event):
        # Send delete event to WebSocket
        self.send(text_data=json.dumps({
            'type': 'delete',
            'message_id': event['message_id'],
        }))
