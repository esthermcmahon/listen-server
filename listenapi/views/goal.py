"""View module for handling requests about goals"""
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import status
from listenapi.models import Excerpt, Recording, Musician, Goal, Category, category
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class MusicianSerializer(serializers.ModelSerializer):
    """Serializer for Musician info from an excerpt"""
    user = UserSerializer(many=False)
    class Meta:
        model = Musician
        fields = ('id', 'bio', 'user')

class ExcerptSerializer(serializers.ModelSerializer):
    """Serializer for excerpts"""
    musician = MusicianSerializer(many=False)
    class Meta:
        model = Excerpt
        fields = ('id', 'name', 'musician')
        depth = 1

class RecordingSerializer(serializers.ModelSerializer):
    """JSON serializer for recordings"""
    excerpt = ExcerptSerializer(many=False)
    class Meta:
        model = Recording
        fields = ('audio', 'excerpt', 'date', 'label')
        depth = 1

class CategorySerializer(serializers.ModelSerializer):
    """JSON serializer for categories"""
    class Meta:
        model = Category
        fields = ('id', 'label')

class GoalSerializer(serializers.ModelSerializer):
    """Serializer for goals"""
    recording = RecordingSerializer(many=False)
    category = CategorySerializer(many=False)
    class Meta:
        model = Goal
        fields = ('id', 'recording', 'category', 'goal', 'action')

    

class Goals(ViewSet):
    """Request handlers for goals"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /goals POST new goal
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {Number} recording_id Associated recording
        @apiParam {Number} category_id Associated category
        @apiParam {String} goal Goal
        @apiParam {String} action Action
        @apiParamExample {json} Input
            {
                "recording": 1,
                "category": 2,
                "goal": "F# perfectly in tune in measure 4",
                "action": "Start slow, sing in head, then get 3x in a row"
            }
        @apiSuccess (200) {Number} goal.recording Associated recording
        @apiSuccess (200) {Number} goal.category Associated category
        @apiSuccess (200) {String} goal.goal Goal
        @apiSuccess (200) {String} goal.action Action
        @apiSuccessExample {json} Success
            {
                "id": 1,
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
                "category": {
                    "id": 1,
                    "label": "intonation"
                },
                "goal": "F# perfectly in tune in measure 4",
                "action": "Start slow, sing in head, then get 3x in a row"
            
            }
        """
        try:
            new_goal= Goal()
            new_goal.goal = request.data["goal"]
            new_goal.action = request.data["action"]

            related_category = Category.objects.get(pk=request.data["category"])
            new_goal.category = related_category

            related_recording = Recording.objects.get(pk=request.data["recording"])
            new_goal.recording = related_recording

            new_goal.save()

            serializer = GoalSerializer(new_goal, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response({'message': ex.args[0]})
        

    def retrieve(self, request, pk=None):
        """
        @api {GET} /goals/:id GET goal
        @apiParam {id} id Goal Id
        @apiSuccess (200) {Object} goal Created goal
        @apiSuccess (200) {id} goal.id Goal Id
        @apiSuccess (200) {Number} goal.recording Associated recording
        @apiSuccess (200) {Number} goal.category Associated category
        @apiSuccess (200) {String} goal.goal Goal
        @apiSuccess (200) {String} goal.action Action
        @apiSuccessExample {json} Success
            {
                "id": 1,
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
                "category": {
                    "id": 1,
                    "label": "intonation"
                },
                "goal": "F# perfectly in tune in measure 4",
                "action": "Start slow, sing in head, then get 3x in a row"
            
            }
        """

        try:
            goal = Goal.objects.get(pk=pk)
            serializer = GoalSerializer(goal, context={'request': request})
            return Response(serializer.data)
        except Goal.DoesNotExist as ex:
            return HttpResponseServerError(ex, status = status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """
        @api {PUT} /goals/:id PUT changes to Goal
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Goal Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        goal = Goal.objects.get(pk=pk)
        goal.goal = request.data["goal"]
        goal.action = request.data["action"]

        related_category = Category.objects.get(pk=request.data["category"])
        goal.category = related_category

        related_recording = Recording.objects.get(pk=request.data["recording"])
        goal.recording = related_recording
        
        goal.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /goal/:id DELETE goal
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Goal Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            goal = Goal.objects.get(pk=pk)
            goal.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Goal.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def list(self, request):
        """
        @api {GET} /goals GET all goals
        @apiSuccess (200) {Object[]} goals Array of goals
        @apiSuccessExample {json} Success
            [
                {
                "id": 1,
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
                "category": {
                    "id": 1,
                    "label": "intonation"
                },
                "goal": "F# perfectly in tune in measure 4",
                "action": "Start slow, sing in head, then get 3x in a row"
            
            }
            
            ]
        """
        goals = Goal.objects.all()

        # Support filtering
        recording = self.request.query_params.get('recording', None)

        if recording is not None:
            goals = goals.filter(recording=recording)
        
        serializer = GoalSerializer(
            goals, many=True, context={'request': request})
        return Response(serializer.data)

        

    