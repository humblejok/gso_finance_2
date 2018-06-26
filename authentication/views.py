from rest_framework.views import View
from django.http import HttpResponse, JsonResponse
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
        logout(request)
        return HttpResponse(status=200)

    def post(self, request):
        # loading the json data found in the request's body
        user = json.loads(request.body.decode('utf-8'))
        # using django authentication method with loaded data
        auth_user = authenticate(
            request, username=user['username'], password=user['password'])
        if auth_user is not None:
            login(request, auth_user)
            # requesting token for specific user
            r_tok = self.getToken(user['username'], user['password'])
            # returning json response to the front-end containing jwtok and it's refresh value
            return JsonResponse({
                'access': r_tok.json()['access'],
                'refresh': r_tok.json()['refresh']
            })
        return HttpResponse

    def getToken(self, _username, _password):
        '''
        Method used to pass user info in a POST request in order to obtain a JWToken
        '''
        data = {'username': _username, 'password': _password}
        r = requests.post('http://jiren:8001/api/token/', data=data)
        return r

@method_decorator(csrf_exempt, name='dispatch')
class csrfPostTest(View):

    def get(self, request):
        print('CsrfGetTest View')
        response = HttpResponse(status=200)
        response['Set-Cookie'] = 'my-cookie=om-nom-nom'
        response['Access-Control-Allow-Origin'] = 'http://jiren:4200'
        response['X-Frame-Options'] = 'ALLOW-FROM http://jiren:4200'
        return response

    def post(self, request):
        print('CsrfPostTest View')
        return HttpResponse(status=200)
