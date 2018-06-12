from rest_framework.views import View
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
import json

@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(View):

    def post(self, request):
        value = False
        user = json.loads(request.body.decode('utf-8'))
        user = authenticate(request, username=user['username'], password=user['password'])
        if user is not None:
            #login(request, user)
            value = True
        response = HttpResponse(status=200)
        return redirect('http://localhost:4200/')
