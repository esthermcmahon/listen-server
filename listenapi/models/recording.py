""" Recording model module"""
from django.db import models
from django.db.models.deletion import DO_NOTHING, SET_NULL
from django.db.models.query import FlatValuesListIterable


class Recording(models.Model):
    """Recording database model"""
    audio = models.CharField(max_length=1000)
    excerpt = models.ForeignKey("Excerpt", on_delete=SET_NULL, null=True)
    date = models.DateField(auto_now_add=False)
    label = models.CharField(max_length=500)
   
    