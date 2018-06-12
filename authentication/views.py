from rest_framework.views import View
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(View):
    response = HttpResponse()

    def post(self, request):
        print(request)
        user = request.username
        print(user)
        user = authenticate(request, username=user, password=user)
        if user is not None:
            #login(request, user)
            # Redirect to a success page.
            print('y')
            return self.response
        else:
            # Return an 'invalid login' error message.
            print('n')
            return self.response
