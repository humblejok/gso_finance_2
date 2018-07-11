from .models import ObfuscationCipher
import re

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
            searchOrdDict = re.search( r'OrderedDict', str(item))
            childOrdDict = re.search( r'OrderedDict', str(collection[item]))
            if searchOrdDict or childOrdDict:
                 print(item)
            #    self.getChildItem(item)
            #elif item != 'access' and item != 'refresh':
            #    collection[item] = self.OCIPH.cipher_controller(collection[item])                
        return
