from .models import ObfuscationCipher
import collections

class DataObfuscationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):
        if hasattr(response, 'content_type'):
            OCIPH = ObfuscationCipher()
            for index, item in enumerate(response.data):
                print('---------------------------')
                print(index)
                print(item)
                item_value = response.data[item]
                if isinstance(item_value, collections.OrderedDict):
                    print('collection')
                else:
                    print('other type')
                if item == 'access':
                    response.data[item] = OCIPH.cipher_controller(response.data[item])
        return response

    def getChildItem(self):
        pass