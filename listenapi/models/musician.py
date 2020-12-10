"""musician model module"""
from django.db import models
from django.contrib.auth.models import User

class Musician(models.Model):
    """Musician database model"""
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    bio=models.CharField(max_length=500, default="")


    @property
    def is_current_user(self):
        return self.__is_current_user

    @is_current_user.setter
    def is_current_user(self,value):
        self.__is_current_user = value
    
