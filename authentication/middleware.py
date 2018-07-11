from .models import ObfuscationCipher
import re, collections

class DataObfuscationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.OCIPH = ObfuscationCipher()

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'data'):
            self.getChildItem(response.data)
        return response

    def getChildItem(self, collection):
        for index, item in enumerate(collection):
            if type(item) is collections.OrderedDict:
                for i_index, i_item in enumerate(item):
                    if type(item[i_item]) is collections.OrderedDict:
                        self.getChildItem(item[i_item])
                    else:
                        pass
                        #item[i_item] = self.OCIPH.cipher_controller(item[i_item])
            elif item != 'access' and item != 'refresh':
                pass
                #collection[item] = self.OCIPH.cipher_controller(collection[item])
            else:
                print('watwat')
        return
