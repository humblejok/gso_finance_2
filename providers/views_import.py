'''
Created on 6 sept. 2018

@author: sdejo
'''
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from json import loads
from security.serializers import SecuritySerializer
from django.http.response import HttpResponse, HttpResponseBadRequest
from security.models import Security

@csrf_exempt
@require_http_methods(["POST"])
def security(request):
    json_security = loads(request.body.decode('utf-8'))
    existing_security = Security.objects.filter(identifier=json_security['identifier'], provider__provider_code=json_security['provider'])
    update = existing_security.exists() and existing_security.count()==1
    if update:
        json_security['id'] = existing_security[0].id
    elif existing_security.count()>1:
        return HttpResponse(status=409)
    finance_security = SecuritySerializer(data=json_security)
    valid = finance_security.is_valid()
    if valid:
        if update:
            finance_security.update(existing_security[0], finance_security.validated_data)
        else:
            finance_security.save()
    else:
        return HttpResponseBadRequest('Invalid data')
    return HttpResponse(status=200)