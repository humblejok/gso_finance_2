from rest_framework.views import View
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(View):
    response = HttpResponse()

    def post(self, request):
        user = json.loads(request.body.decode('utf-8'))
        user = authenticate(request, username=user['username'], password=user['password'])
        if user is not None:
            login(request, user)
            self.response['feedback'] = 'success'
        else:
            self.response['feedback'] = 'failure'
        return self.response
