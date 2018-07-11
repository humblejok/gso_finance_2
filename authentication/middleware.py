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
            print(type(item))
            #    print(item)
            if type(item) is collections.OrderedDict:
                print(collection[item])
            #    if type(collection[item]) is collections.OrderedDict:
            #        self.getChildItem(item)
            #elif type(item) is collections.OrderedDict:
            #        self.getChildItem(item)
            #elif item != 'access' and item != 'refresh':
            #elif item=='quick_access':
            #else:
            #    collection[item] = self.OCIPH.cipher_controller(collection[item])
                #print(item)
                #print(collection[item])
        return
