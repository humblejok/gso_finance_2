from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#from rest_framework import authentication, permissions
from django.contrib.auth.models import User

class ListUsers(APIView):
    #authentication_classes = (authentication.TokenAuthentication,)
    #permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)

    def post(self):
        pass