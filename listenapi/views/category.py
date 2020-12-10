"""View module for handling requests about categories"""
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import status
from listenapi.models import Category
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser

class CategorySerializer(serializers.ModelSerializer):
    """JSON serializer for categories"""
    class Meta:
        model = Category
        fields = ('id', 'label')

class Categories(ViewSet):
    """Request handlers for categories"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /categories POST new category
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {String} label Category label
        @apiParamExample {json} Input
            {
                "label": "Intonation"
            }
        @apiSuccess (200) {Object} category Created category
        @apiSuccess (200) {id} category.id Category Id
        @apiSuccess (200) {String} category.label Category label
        @apiSuccessExample {json} Success
            {
                "id": 1,
                "label": "intonation"
                
            }
        """
        try:
            new_category = Category()
            new_category.label = request.data["label"]

            new_category.save()

            serializer = CategorySerializer(new_category, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as ex:
            return Response({'message': ex.args[0]})
        
    def update(self, request, pk=None):
        """
        @api {PUT} /categories/:id PUT changes to category
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Category Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        category = Category.objects.get(pk=pk)
        category.label = request.data["label"]

        category.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /categories/:id DELETE category
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        @apiParam {id} id Category Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            category = Category.objects.get(pk=pk)
            category.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Category.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def list(self, request):
        """
        @api {GET} /categories GET all categories
        @apiSuccess (200) {Object[]} comments Array of categories
        @apiSuccessExample {json} Success
            [
                {
                "id": 1,
                "label": "Intonation"
                },
                "id": 1,
                "label": "Rhythm"
                }
            ]
        """
        categories = Category.objects.all()

        serializer = CategorySerializer(
            categories, many=True, context={'request': request})
        return Response(serializer.data)

        

    