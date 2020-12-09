""" Goal model module """
from django.db import models

class Goal(models.Model):
    """Goal database model"""
    recording=models.ForeignKey("Recording", on_delete=models.SET_NULL, null=True, related_name="recording_goal")
    category =models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, related_name="category")
    goal = models.CharField(max_length=500)
    action=models.CharField(max_length=500)
   