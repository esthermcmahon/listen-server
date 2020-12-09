"""Connection model module"""
from django.db import models


class Connection(models.Model):
    """Connection database model"""
    practicer = models.ForeignKey("Musician", on_delete=models.SET_NULL, null=True, related_name="practicer_to_follow")
    follower = models.ForeignKey("Musician", on_delete=models.SET_NULL, null=True, related_name="follower")
    created_on = models.DateField(auto_now=False, auto_now_add=False)
    ended_on = models.DateField(auto_now=False, auto_now_add=False, null=True)

    
