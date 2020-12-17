"""Excerpt model module"""
from django.db import models


class Excerpt(models.Model):
    """Excerpt database model"""
    name = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    musician = models.ForeignKey("Musician", on_delete=models.SET_NULL, null=True, related_name="practicer")


    @property
    def created_by_current_user(self):
        return self.__created_by_current_user

    @created_by_current_user.setter
    def created_by_current_user(self, value):
        self.__created_by_current_user = value
