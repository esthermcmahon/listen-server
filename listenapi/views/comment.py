"""View module for handling requests about comments"""
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import status
from listenapi.models import Recording, Musician, Comment, Excerpt
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')

class MusicianSerializer(serializers.ModelSerializer):
    """Serializer for Musician info from a recording"""
    user = UserSerializer(many=False)
    class Meta:
        model = Musician
        fields = ('id', 'bio', 'user')

class ExcerptSerializer(serializers.ModelSerializer):
    """Serializer for excerpts"""
    class Meta:
        model = Excerpt
        fields = ('id', 'name')

class RecordingSerializer(serializers.ModelSerializer):
    """JSON serializer for recordings"""
    excerpt = ExcerptSerializer(many=False)
    class Meta:
        model = Recording
        fields = ('audio', 'excerpt', 'date', 'label')
        depth = 2

class CommentSerializer(serializers.ModelSerializer):
    """JSON serializer for comments"""
    author = MusicianSerializer(many=False)
    recording = RecordingSerializer(many=False)
    class Meta:
        model= Comment
        fields= ('id', 'author', 'recording', 'date', 'content')
        depth= 2

class Comments(ViewSet):
    """Request handlers for comments"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /comments POST new comment
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {Number} author Musician who created comment
        @apiParam {Number} recording Associated recording
        @apiParam {Date} date Date created
        @apiParam {String} content Content of comment
        @apiParamExample {json} Input
            {
                "author": 1,
                "recording": 1,
                "date": "2020-12-09",
                "content": "Make sure you can sing it before you play it"
            }
        @apiSuccess (200) {Object} comment Created comment
        @apiSuccess (200) {id} comment.id Comment Id
        @apiSuccess (200) {Number} comment.author Musician who created comment
        @apiSuccess (200) {Number} comment.recording Associated recording
        @apiSuccess (200) {Date} comment.date Date created
        @apiSuccess (200) {String} comment.content Content of comment
        @apiSuccessExample {json} Success
            {
                "id": 1,
                "author": {
                    "id": 1,
                    "bio": "violinist",
                    "user": {
                        "id": 1,
                        "username": "estherviolin"
                    }

                },
                "recording": {
                    "id": 1,
                    "audio": "urlstring",
                    "date": "2020-12-09"
                    "label": "Mozart 5 take 1",
                    "excerpt": {
                        "name": "Mozart 5",
                        "done": False,
                        "musician": 1
                    }
                },
                "date": "2020-12-09",
                "content": "Make sure you can sing it before you play it"
                
            }
        """
        try:
            new_comment = Comment()
            new_comment.content = request.data["content"]
            new_comment.date = request.data["date"]

            related_recording = Recording.objects.get(pk=request.data["recording"])
            new_comment.recording = related_recording

            author = Musician.objects.get(user=request.auth.user)
            new_comment.author = author

            new_comment.save()

            serializer = CommentSerializer(new_comment, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as ex:
            return Response({'message': ex.args[0]})
        

    def update(self, request, pk=None):
        """
        @api {PUT} /comments/:id PUT changes to comment
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Comment Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        comment = Comment.objects.get(pk=pk)
        comment.content = request.data["content"]
        comment.date = request.data["date"]

        related_recording = Recording.objects.get(pk=request.data["recording"])
        comment.recording = related_recording

        author = Musician.objects.get(user=request.auth.user)
        comment.author = author

        comment.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /comments/:id DELETE comment
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Comment Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            comment = Comment.objects.get(pk=pk)
            comment.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Comment.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def list(self, request):
        """
        @api {GET} /comments GET all comments
        @apiSuccess (200) {Object[]} comments Array of comments
        @apiSuccessExample {json} Success
            [
                {
                "id": 1,
                "author": {
                    "id": 1,
                    "bio": "violinist",
                    "user": {
                        "id": 1,
                        "username": "estherviolin"
                    }

                },
                "recording": {
                    "id": 1,
                    "audio": "urlstring",
                    "date": "2020-12-09"
                    "label": "Mozart 5 take 1",
                    "excerpt": {
                        "name": "Mozart 5",
                        "done": False,
                        "musician": 1
                    }
                },
                "date": "2020-12-09",
                "content": "Make sure you can sing it before you play it"
                
                }
            ]
        """
        comments = Comment.objects.all()
        recordings = Recording.objects.all()

        # Support filtering
        recording = self.request.query_params.get('recording', None)

        if recording is not None:
            recordings = recordings.filter(recording_id = recording)

        

        serializer = CommentSerializer(
            comments, many=True, context={'request': request})
        return Response(serializer.data)

        

    