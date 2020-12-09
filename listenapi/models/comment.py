"""Comment model module"""
from django.db import models


class Comment(models.Model):
    """Comment database model"""
    author = models.ForeignKey("Musician", on_delete=models.SET_NULL, null=True, related_name="author")
    recording = models.ForeignKey("Recording", on_delete=models.SET_NULL, null=True, related_name="recording_comment")
    date = models.DateField(auto_now_add=False)
    content = models.CharField(max_length=500)
    

    
