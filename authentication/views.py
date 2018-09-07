from rest_framework.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from random import randint
import json
import requests
import hashlib
from gso_finance_2.settings import EXTERNAL_HOST_NAME


@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(View):

    def post(self, request):
        # loading the json data found in the request's body
        user = json.loads(request.body.decode('utf-8'))
        # using django authentication method with loaded data
        auth_user = authenticate(request, username=user['username'], password=user['password'])
        if auth_user is not None:
            login(request, auth_user)
            # requesting token for specific user
            r_tok = self.getToken(user['username'], user['password'])
            # creating session ID depending on user status
            if auth_user.is_superuser:
                salt = 42
            else:
                i = randint(0, 1)
                if(i == 0):
                    salt = randint(0, 41)
                else:
                    salt = randint(43, 99)
            session_id = self.hashingFunc(r_tok.json()['refresh'], salt)
            # returning json response to the front-end containing jwtok and it's refresh value
            return JsonResponse({
                'access': r_tok.json()['access'],
                'refresh': r_tok.json()['refresh'],
                'session_id': session_id
            })
        return HttpResponse(status=403)

    def getToken(self, _username, _password):
        '''
        Method used to pass user info in a POST request in order to obtain a JWToken
        '''
        data = {'username': _username, 'password': _password}
        r = requests.post(EXTERNAL_HOST_NAME + '/api/token/', data=data)
        return r

    def hashingFunc(self, _value, _salt):
        h = hashlib.sha256((_value + str(_salt)).encode('utf-8'))
        return h.hexdigest()