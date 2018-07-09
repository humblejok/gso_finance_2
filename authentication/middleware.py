from .models import ObfuscationCipher
import re

class DataObfuscationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'data'):
            self.getChildItem(response.data)
        return response

    def getChildItem(self, collection):
        OCIPH = ObfuscationCipher()
        for index, item in enumerate(collection):
                print('---------------------------')
                print(index)
                #print(item)

                searchOrdDict = re.search( r'OrderedDict', str(item))
                if searchOrdDict:
                    #self.getChildItem(item)
                    for elem in enumerate(collection):
                        print(elem)
                else:
                    return
                    #print(collection[item])
                    #collection[item] = OCIPH.cipher_controller(collection[item])

                if item == 'access':
                    collection[item] = OCIPH.cipher_controller(collection[item])
        return