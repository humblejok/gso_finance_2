from django.conf import settings

class DataObfuscationMiddleware:

    def __init__(self, get_response):
        print(get_response)
        pass
