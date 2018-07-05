from django.conf import settings
from pprint import pprint

class DataObfuscationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):
        #pprint(dir(response))
        if hasattr(response, 'content_type'):
            pprint(response.data['OrderedDict'])
        else:
            pprint('bar')
        return response