"""View module for handling requests about connections"""
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import status
from datetime import date
from listenapi.models import Musician, Connection
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')

class MusicianSerializer(serializers.ModelSerializer):
    """Serializer for Musician info in a connection"""
    user = UserSerializer(many=False)

    class Meta:
        model = Musician
        fields = ('id', 'bio', 'user')

class ConnectionSerializer(serializers.ModelSerializer):
    """Serializer for connections"""
    practicer = MusicianSerializer(many=False)
    follower = MusicianSerializer(many=False)
    class Meta:
        model = Connection
        fields = ('id', 'practicer', 'follower', 'created_on', 'ended_on')
        depth = 2

class Connections(ViewSet):
    """Request handlers for excerpts"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /connections POST new connection
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {Number} practicer Musician to follow
        @apiParam {Number} follower Follower
        @apiParam {Date} created_on 
        @apiParam {Date} ended_on
        @apiParamExample {json} Input
            {
                "practicer": 1,
                "follower": 1,
                "created_on": "2020-12-09"
                "ended_on": Null
            }
        @apiSuccess (200) {Object} connection Created connection
        @apiSuccess (200) {id} connection.id Connection Id
        @apiSuccess (200) {Number} connection.practicer Associated musician
        @apiSuccess (200) {Number} connection.follower Associated musician
        @apiSuccess (200) {Date} created_on 
        @apiSuccess (200) {Date} ended_on
        @apiSuccessExample {json} Success
            {
                "id": 1,
                "practicer": {
                    "id": 1,
                    "bio": "violinist",
                    "user": {
                        "id": 1,
                        "first_name": "Esther",
                        "last_name": "Sanders",
                        "email": "esther@esther.com",
                        "username": "estherviolin"
                    }
                },
                "follower": {
                    "id": 1,
                    "bio": "violinist",
                    "user": {
                        "id": 1,
                        "first_name": "Esther",
                        "last_name": "Sanders",
                        "email": "esther@esther.com",
                        "username": "estherviolin"
                    }
                },
                "created_on": "2020-12-09",
                "ended_on": Null
        
            }
        """
        try:
            new_connection = Connection()
            new_connection.created_on = request.data['created_on']
            new_connection.ended_on = request.data['ended_on']

            related_practicer = Musician.objects.get(pk=request.data["practicer"])
            new_connection.practicer = related_practicer

            # user = Musician.objects.get(user=request.auth.user)
            # new_connection.follower = user

            related_follower = Musician.objects.get(pk=request.data['follower'])
            new_connection.follower = related_follower

            new_connection.save()

            serializer = ConnectionSerializer(new_connection, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({'message': ex.args[0]})

    def list(self, request):

        connections = Connection.objects.all()

        serializer = ConnectionSerializer(connections, many=True, context={'request': request})
            
        return Response(serializer.data)
        

    @action(methods = ['get', 'put'], detail=True)
    def unfollow(self, request, pk=None):
        if request.method == 'PUT':

            practicer = Musician.objects.get(pk=pk)

            connection = Connection.objects.get(practicer=practicer, follower = request.auth.user.id, ended_on = None)

            connection.ended_on = date.today()
            connection.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)