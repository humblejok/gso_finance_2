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
            for index, item in enumerate(response.data):
                self.getChildItem(item)
        return response

    def getChildItem(self, var):
        if type(var) is list:
            for i in range(0, len(var)):
                self.getChildItem(var[i])
        elif type(var) is dict or type(var) is collections.OrderedDict:
            for key, value in enumerate(var):
                self.getChildItem(var[value])
        else:
            print(type(var))
        return
        '''
        for index, item in enumerate(collection):
            if type(item) is collections.OrderedDict:
                for i_index, i_item in enumerate(item):
                    if type(item[i_item]) is collections.OrderedDict:
                        self.getChildItem(item[i_item])
                    else:
                        pass
                        # item[i_item] = self.OCIPH.cipher_controller(item[i_item])
            elif item != 'access' and item != 'refresh':
                print(type(collection[item]))
                # collection[item] = self.OCIPH.cipher_controller(collection[item])
            else:
                print('watwat')
        return
        '''
