"""Comment model module"""
from django.db import models


class Comment(models.Model):
    """Comment database model"""
    author = models.ForeignKey("Musician", on_delete=models.SET_NULL, null=True, related_name="author")
    recording = models.ForeignKey("Recording", on_delete=models.SET_NULL, null=True, related_name="recording_comment")
    date = models.DateField(auto_now_add=False)
    content = models.CharField(max_length=500)
    

    @property
    def created_by_current_user(self):
        return self.__created_by_current_user

    @created_by_current_user.setter
    def created_by_current_user(self, value):
        self.__created_by_current_user = value

