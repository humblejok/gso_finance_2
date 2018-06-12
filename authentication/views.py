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

    def get(self, request):
        print(request)
        return self.response

    def post(self, request):
        print(request)
        #username = request.POST['user']['username']
        #password = request.POST['user']['password']
        user = authenticate(request, username='alice', password='cooperStalker')
        if user is not None:
            #login(request, user)
            # Redirect to a success page.
            print('y')
            return self.response
        else:
            # Return an 'invalid login' error message.
            print('n')
            return self.response

'''
form = self.form_class(request.POST)
if form.is_valid():
    user = form.save(commit=False)
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    user.set_password(password)
    user.save()
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            self.login(request, user)
            return self.redirect('index')
    return render(request, self.template_name, {'form': form})
'''
