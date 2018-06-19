from rest_framework.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(View):

    def get(self, request):
        print('get request -> logout')
        logout(request)
        return HttpResponse(status=200)

    def post(self, request):
        if request.user.is_authenticated:
            print('User Is Authenticated')
        else:
            user = json.loads(request.body.decode('utf-8'))
            auth_user = authenticate(
                request, username=user['username'], password=user['password'])
            if auth_user is not None:
                login(request, user)
                serializer = self.serializer_class(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return HttpResponse(status=200)


class csrfPostTest(View):

    def post(self, request):
        print('CsrfPostTest View')
        return HttpResponse(status=200)
