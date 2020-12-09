"""musician model module"""
from django.db import models
from django.contrib.auth.models import User

class Musician(models.Model):
    """Musician database model"""
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    bio=models.CharField(max_length=500, default="")

    
