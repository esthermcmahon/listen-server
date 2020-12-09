"""Excerpt model module"""
from django.db import models


class Excerpt(models.Model):
    """Excerpt database model"""
    name = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    musician = models.ForeignKey("Musician", on_delete=models.SET_NULL, null=True, related_name="practicer")


    
