"""View module for handling requests about musicians"""
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from listenapi.models import Musician

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

class MusicianSerializer(serializers.ModelSerializer):
    """Serializer for Musicians"""
    user = UserSerializer(many=False)

    class Meta:
        model = Musician
        fields = ('id', 'bio', 'user', 'is_current_user')

class Musicians(ViewSet):
    """Request handlers for musicians"""

    def list(self, request):
        """ handles GET all"""
        musicians = Musician.objects.all()

        serializer = MusicianSerializer(musicians, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single musician
        Returns:
            Response -- JSON serialized musician instance
        """
       
        try:
            musician = Musician.objects.get(pk=pk)
            
            #logic to set an unmapped property on Musician
            #will let front end determine if the Musicianretrieved by this function is the current user

            if request.auth.user.id == int(pk):
                musician.is_current_user = True
            else:
                musician.is_current_user = False

            serializer = MusicianSerializer(musician, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /musicians/:id PUT changes to musician profile
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Musician Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        musician = Musician.objects.get(user=request.auth.user)
        musician.user.first_name = request.data["first_name"]
        musician.user.last_name = request.data["last_name"]
        musician.user.username = request.data["username"]
        musician.user.email = request.data["email"]
        
        musician.user.save()
        musician.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
