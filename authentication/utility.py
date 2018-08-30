'''
Created on 30 août 2018

@author: sdejo
'''
from django.utils.functional import SimpleLazyObject
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication,\
    JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

#from rest_framework.request from Request
class AuthenticationMiddlewareJWT(object):
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ")
        data = {'user_id': token}
        print(token)
        try:
            valid_data = JWTTokenUserAuthentication().get_user(data)
            t = JWTAuthentication()
            valid_data.get_username()
            user = valid_data['user']
            request.user = user
        except InvalidToken as iv:
            print("Invalid token", iv)
            

        return self.get_response(request)