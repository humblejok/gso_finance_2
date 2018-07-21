from rest_framework.utils.serializer_helpers import ReturnList
from django.conf import settings
from .models import ObfuscationCipher
import re
import collections

EXEMPT_URLS = [re.compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'CRYPT_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(url) for url in settings.CRYPT_EXEMPT_URLS]

class DataObfuscationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.OCIPH = ObfuscationCipher()

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        path = request.path_info.lstrip('/')
        if any(url.match(path) for url in EXEMPT_URLS):
            return response
        elif hasattr(response, 'data'):
            print(response.data[0])
            '''
            for i in range(0, len(response.data)):
                if 'inception_date' in response.data[i]:
                    response.data[i]['inception_date'] = self.OCIPH.cipher_controller(response.data[i]['inception_date'])
                if 'current_aum_local' in response.data[i]:
                    response.data[i]['current_aum_local'] = self.OCIPH.cipher_controller(response.data[i]['current_aum_local'])
                if 'current_aum_mgmt' in response.data[i]:
                    response.data[i]['current_aum_mgmt'] = self.OCIPH.cipher_controller(response.data[i]['current_aum_mgmt'])
            '''
        return response
'''
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
            #print(var)
            print(self.OCIPH.cipher_controller(var))
        return
'''