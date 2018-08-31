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
        authenticator = JWTAuthentication()
        token = authenticator.get_header(request)
        request.user = None
        if token!=None:
            raw_token = authenticator.get_raw_token(token)
            if raw_token != None:
                try:
                    validated_token = authenticator.get_validated_token(raw_token)
                    request.user = authenticator.get_user(validated_token)
                except InvalidToken:
                    print("Invalid token")

        return self.get_response(request)