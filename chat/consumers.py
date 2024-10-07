import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Message
from courses.models import Course
import uuid

'''database operation should done in sync way
   Websocket sending and reciving should done in async way nonblocking operation'''

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Getting current user
        self.user = self.scope['user']
        # Getting course id from URL
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'chat_{self.id}'
        
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        # Accept connection
        await self.accept()
        
        # Send previous messages
        previous_messages = await self.get_previous_messages()
        for message in previous_messages:
            await self.send(text_data=json.dumps(message))
        
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json['type'] == 'message':
            await self.handle_message(text_data_json['message'])
        elif text_data_json['type'] == 'delete':
            await self.handle_delete(text_data_json['message_id'])

    async def handle_message(self, message):
        now = timezone.now()
        message_id = str(uuid.uuid4())  # Generate a new UUID for the message
        await self.save_message(message_id, message, now)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'message_id': message_id,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )

    async def handle_delete(self, message_id):
        # Delete message and send delete event to room group
        await self.delete_message(message_id)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_delete',
                'message_id': message_id,
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def chat_delete(self, event):
        # Send delete event to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'delete',
            'message_id': event['message_id'],
        }))

    async def save_message(self, message_id, message, now):
        course = await database_sync_to_async(Course.objects.get)(id=self.id)
        await database_sync_to_async(Message.objects.create)(
            course=course,
            user=self.user,
            message=message,  
            timestamp=now,
            message_id=message_id,
        )
        
    async def delete_message(self, message_id):
        await database_sync_to_async(Message.objects.filter(message_id=message_id).update)(deleted=True)
    
    # we cannot force the synchronous process in async process we should handle async and sync both seperately
    async def get_previous_messages(self):
        # Fetch previous messages in an async context
        messages = await database_sync_to_async(self.fetch_previous_messages)()
        return messages

    def fetch_previous_messages(self):
        # This method runs in a synchronous context
        messages = Message.objects.filter(course=self.id, deleted=False).order_by('-timestamp')[:50][::-1]
        return [
            {
                'message_id': str(msg.message_id), 
                'message': msg.message,
                'user': msg.user.username,
                'datetime': msg.timestamp.isoformat(),
                'deleted': msg.deleted
            } for msg in messages
        ]


    
