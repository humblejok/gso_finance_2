from rest_framework.views import View
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


class UserLogin(View):

    def get(self, request):
        print('g')
        #form = self.form_class(None)
        #return render(request, self.template_name, {'form': form})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            print('y')
        else:
            # Return an 'invalid login' error message.
            print('n')

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
