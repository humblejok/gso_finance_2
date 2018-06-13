from rest_framework.views import View
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(View):

    def post(self, request):
        if request.user.is_authenticated:
            print('User Is Authenticated')
        else:
            user = json.loads(request.body.decode('utf-8'))
            if authenticate(request, username=user['username'], password=user['password']):
                auth_user = authenticate(request, username=user['username'], password=user['password'])
                if auth_user is not None:
                    if login(request, auth_user):
                        print('User Logged In')
                    else:
                        print('Failure: login')
                else:
                    print('Invalid Credentials')
            else:
                print('Failure: Authenticate')
        return HttpResponse(status=200)
