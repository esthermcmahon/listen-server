'''Handles the authentication of a user'''
import json
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from listenapi.models import Musician



@csrf_exempt
def login_user(request):
    '''Handles the authentication of a musician
    Method arguments:
      request -- The full HTTP request object
    '''

    req_body = json.loads(request.body.decode())

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':

        # Use the built-in authenticate method to verify
        username = req_body['username']
        password = req_body['password']
        authenticated_user = authenticate(username=username, password=password)

        # If authentication was successful, respond with their token
        if authenticated_user is not None:
            token = Token.objects.get(user=authenticated_user)
            data = json.dumps({"valid": True, "token": token.key})
            return HttpResponse(data, content_type='application/json')

        else:
            # Bad login details were provided. So we can't log the user in.
            data = json.dumps({"valid": False})
            return HttpResponse(data, content_type='application/json')
    
    return HttpResponseNotAllowed(permitted_methods=['POST'])


@csrf_exempt
def register_user(request):
    '''Handles the creation of a new gamer for authentication
    Method arguments:
      request -- The full HTTP request object
    '''

    # Load the JSON string of the request body into a dict
    req_body = json.loads(request.body.decode())

    # Create a new user by invoking the `create_user` helper method
    # on Django's built-in User model
    new_user = User.objects.create_user(
        username=req_body['username'],
        email=req_body['email'],
        password=req_body['password'],
        first_name=req_body['first_name'],
        last_name=req_body['last_name']
    )

    musician = Musician.objects.create(
        bio=req_body['bio'],
        user=new_user
    )
    #Save new musician to the database
    musician.save()

    # Use the REST Framework's token generator on the new user account
    token = Token.objects.create(user=new_user)

    # Return the token to the client
    data = json.dumps({"token": token.key})
    return HttpResponse(data, content_type='application/json', status=status.HTTP_201_CREATED)

#Patrick's profile and token
    
#         {
#             "bio": "",
#             "user": {
#                 "password": "pbkdf2_sha256$216000$qMRH8szID7Z8$Vljya2V3XfruOHuvx1hGz9ZyKg4bxbw7rc2WO0gTR7I=",
#                 "last_login": null,
#                 "is_superuser": false,
#                 "username": "patrickcello1",
#                 "first_name": "Patrick",
#                 "last_name": "Rush",
#                 "email": "patrick@patrick.com",
#                 "is_staff": true,
#                 "is_active": true,
#                 "date_joined": "2020-08-28T14:51:39.989Z",
#                 "groups": [],
#                 "user_permissions": []   
#             }
#     }

#     {
#     "token": "d15deaece8effacf9926abb512732754f0f1b4b4"
# }