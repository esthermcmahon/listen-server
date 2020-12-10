"""View module for handling requests about recordings"""
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import status
from listenapi.models import Recording, Excerpt, Musician
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class MusicianSerializer(serializers.ModelSerializer):
    """Serializer for Musician info from a recording"""
    user = UserSerializer(many=False)
    class Meta:
        model = Musician
        fields = ('id', 'bio', 'user')

class ExcerptSerializer(serializers.ModelSerializer):
    """Serializer for excerpt info from a recording"""
    musician = MusicianSerializer(many=False)
    class Meta:
        model = Excerpt
        fields = ('id', 'name', 'musician')

class RecordingSerializer(serializers.ModelSerializer):
    """JSON serializer for recordings"""
    excerpt = ExcerptSerializer(many=False)
    class Meta:
        model = Recording
        fields = ('id', 'audio', 'excerpt', 'date', 'label')
        depth = 2


class Recordings(ViewSet):
    """Request handlers for Recordings"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /recordings POST new recording
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {String} audio String of url blob or cloudinary link
        @apiParam {Number} excerpt_id Excerpt being recorded
        @apiParam {Date} date Date created
        @apiParam {String} label Name of recording
        @apiParamExample {json} Input
            {
                "audio": "urlstring",
                "excerpt_id": 1,
                "date": "2020-12-09",
                "label": "Mozart 5 take 1"
            }
        @apiSuccess (200) {Object} recording Created recording
        @apiSuccess (200) {id} recording.id Recording Id
        @apiSuccess (200) {String} recording.audio String of url blob or cloudinary link
        @apiSuccess (200) {Number} recording.excerpt_id Associated excerpt
        @apiSuccess (200) {Date} recording.date Date created
        @apiSuccess (200) {String} recording.label Name of recording
        @apiSuccessExample {json} Success
            {
                "id": 1,
                "audio": "urlstring",
                "date": "2020-12-09"
                "label": "Mozart 5 take 1",
                "excerpt": {
                    "name": "Mozart 5",
                    "done": False,
                    "musician": 1
                }
            }
        """
        try:
            new_recording = Recording()
            new_recording.audio = request.data["audio"]
            new_recording.date = request.data["date"]
            new_recording.label = request.data["label"]

            related_excerpt = Excerpt.objects.get(pk=request.data["excerpt"])
            new_recording.excerpt = related_excerpt

            new_recording.save()

            serializer = RecordingSerializer(new_recording, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as ex:
            return Response({'message': ex.args[0]})
        

    def retrieve(self, request, pk=None):
        """
        @api {GET} /recordings/:id GET recording
        @apiParam {id} id Recording Id
        @apiSuccess (200) {Object} recording Created recording
        @apiSuccess (200) {id} recording.id Recording Id
        @apiSuccess (200) {String} recording.audio String of url blob or cloudinary link
        @apiSuccess (200) {Number} recording.excerpt_id Associated excerpt
        @apiSuccess (200) {Date} recording.date Date created
        @apiSuccess (200) {String} recording.label Name of recording
        @apiSuccessExample {json} Success
            {
                "id": 1,
                "audio": "urlstring",
                "date": "2020-12-09"
                "label": "Mozart 5 take 1",
                "excerpt": {
                    "name": "Mozart 5",
                    "done": False,
                    "musician": 1
                }
            }
      
        """

        try:
            recording = Recording.objects.get(pk=pk)
            serializer = RecordingSerializer(recording, context={'request': request})
            return Response(serializer.data)
        except Recording.DoesNotExist as ex:
            return HttpResponseServerError(ex, status = status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """
        @api {PUT} /recordings/:id PUT changes to recording
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Recording Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        recording = Recording.objects.get(pk=pk)
        recording.audio = request.data["audio"]
        recording.date = request.data["date"]
        recording.label = request.data["label"]

        related_excerpt= Excerpt.objects.get(pk=request.data["excerpt"])
        recording.excerpt = related_excerpt
        recording.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /recordings/:id DELETE recording
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Recording Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            recording = Recording.objects.get(pk=pk)
            recording.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Recording.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def list(self, request):
        """
        @api {GET} /recordings GET all recordings
        @apiSuccess (200) {Object[]} recordings Array of recordings
        @apiSuccessExample {json} Success
            [
                {
                "id": 1,
                "audio": "urlstring",
                "date": "2020-12-09"
                "label": "Mozart 5 take 1",
                "excerpt": {
                    "name": "Mozart 5",
                    "done": False,
                    "musician": 1
                }
            
            ]
        """
        recordings = Recording.objects.all()
        excerpts = Excerpt.objects.all()

        # Support filtering
        excerpt = self.request.query_params.get('excerpt', None)
        musician = self.request.query_params.get('musician', None)
        

        if excerpt is not None:
            recordings = recordings.filter(excerpt_id = excerpt)

        if musician is not None:
            musician = Musician.objects.get(pk=musician)
            excerpts = excerpts.filter(musician=musician) 
            recordings = []

            for excerpt in excerpts:
                recordings_list = Recording.objects.filter(excerpt=excerpt)

                for recording in recordings_list:
                    recordings.append(recording)
     

        serializer = RecordingSerializer(
            recordings, many=True, context={'request': request})
        return Response(serializer.data)

        

    