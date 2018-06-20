from rest_framework.views import View
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import requests


@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(View):

    def get(self, request):
        print('get request -> logout')
        logout(request)
        return HttpResponse(status=200)

    def post(self, request):
        user = json.loads(request.body.decode('utf-8'))
        auth_user = authenticate(
            request, username=user['username'], password=user['password'])
        if auth_user is not None:
            login(request, auth_user)
            r_tok = self.getToken(user['username'], user['password'])
            print(r_tok.json()['access'])
            data = r_tok.json()['access']
            return Response(data, template_name=None)
            #return HttpResponse(status=200)
        return HttpResponse(status=200)

    def getToken(self, _username, _password):
        data = {}
        data['username'] = _username
        data['password'] = _password
        r = requests.post('http://jiren:8001/api/token/', data = data)
        return r


class csrfPostTest(View):

    def post(self, request):
        print('CsrfPostTest View')
        return HttpResponse(status=200)
