from .models import ObfuscationCipher
import re

class DataObfuscationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'content_type'):
            OCIPH = ObfuscationCipher()
            for index, item in enumerate(response.data):
                print('---------------------------')
                print(index)
                print(item)

                searchOrdDict = re.search( r'OrderedDict', str(item))
                if searchOrdDict:
                    self.getChildItem(item)
                else:
                    print(response.data[item])

                if item == 'access':
                    response.data[item] = OCIPH.cipher_controller(response.data[item])
        return response

    def getChildItem(self, collection):
        print('getChildItem')
        return