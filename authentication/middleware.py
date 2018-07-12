from rest_framework.utils.serializer_helpers import ReturnList
from .models import ObfuscationCipher
import re
import collections


class DataObfuscationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.OCIPH = ObfuscationCipher()

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'data'):
            #self.getChildItem(response.data)
            for key, value in enumerate(response.data):
                if value!='access' or value!='refresh':
                    response.data[value] = self.OCIPH.cipher_controller(response.data[value])
        return response

    def getChildItem(self, var):
        if type(var) is ReturnList:
            for index, item in enumerate(var):
                self.getChildItem(item)
        elif type(var) is list:
            for i in range(0, len(var)):
                self.getChildItem(var[i])
        elif type(var) is dict or type(var) is collections.OrderedDict:
            for key, value in enumerate(var):
                self.getChildItem(var[value])
        else:
            print(self.OCIPH.cipher_controller(var))
        return
