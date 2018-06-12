from rest_framework.views import View, UserForm
from rest_framework.response import Response
from rest_framework import authentication, permissions, status
from django.contrib.auth.models import User

class UserFormView(View):
    form_class = UserForm
    template_name = 'authentication/registration_form.html'

    def get(self, request):
        form = self.form_class(None)
        return self.render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user.set_password(password)
            user.save()

            user = self.authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    self.login(request, user)
                    return self.redirect('index')

        return self.render(request, self.template_name, {'form': form})
