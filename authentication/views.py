from rest_framework.views import View
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
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
            auth_user = authenticate(request, username=user['username'], password=user['password'])
            if auth_user is not None:
                print(request)
                print(auth_user)
                lres = login(request, auth_user)
                if lres:
                    print('User Logged In')
                else:
                    print('Failure: login')
            else:
                print('Invalid Credentials')
        return HttpResponse(status=200)
