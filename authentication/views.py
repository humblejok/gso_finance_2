from rest_framework.views import View
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework import Response, UserSerializer

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
#class UserLogin(View):
class UserLogin(APIView):

    def post(self, request):
        if request.user.is_authenticated:
            print('User Is Authenticated')
        else:
            user = json.loads(request.body.decode('utf-8'))
            user = authenticate(request, username=user['username'], password=user['password'])
            if user is not None:
                login(request, user)
                print('User Logged In')
            else:
                print('Invalid Credentials')
        #return HttpResponse(status=200)
        return Response(UserSerializer(request.user).data)


'''
class AuthView(APIView):
    authentication_classes = (QuietBasicAuthentication,)
 
    def post(self, request, *args, **kwargs):
        login(request, request.user)
        return Response(UserSerializer(request.user).data)
 
    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response({})
'''
