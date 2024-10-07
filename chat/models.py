from django.db import models
from courses.models import Course
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Create your models here.
class Message(models.Model):
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    message_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    deleted = models.BooleanField(default=False)  # New field for soft deletion

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]} ({self.timestamp})"
