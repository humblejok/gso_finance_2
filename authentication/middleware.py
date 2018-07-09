from django.conf import settings
from .models import ObfuscationCipher

class DataObfuscationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):
        #print(dir(response))
        OCIPH = ObfuscationCipher()
        if hasattr(response, 'content_type'):
            for item in enumerate(response.data):
                if item == 'access':
                    #response.data[item] = 'infinite loop !'
                    print(response.data[item])
                    print(OCIPH)
                else:
                    print('nope')
        else:
            print('bar')
        return response