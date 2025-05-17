from django.db import models
from django.contrib.auth.models import User

class UserAlertConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    required_repetitions = models.IntegerField(default=3)
    time_threshold = models.IntegerField(default=300)  # seconds
    is_active = models.BooleanField(default=True)