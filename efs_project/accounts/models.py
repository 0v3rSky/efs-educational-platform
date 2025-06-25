from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import timedelta
from django.utils import timezone

# Create your models here.

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    @classmethod
    def generate_code(cls):
        return ''.join(random.choices(string.digits, k=6))
    
    @classmethod
    def create_code(cls, user):
        # Удаляем старые неиспользованные коды
        cls.objects.filter(user=user, is_used=False).delete()
        
        # Создаем новый код
        code = cls.generate_code()
        return cls.objects.create(user=user, code=code)
    
    def is_valid(self):
        # Код действителен 15 минут
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(minutes=15)
