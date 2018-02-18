from rest_framework import viewsets, generics
from providers.models import ExternalSecurity
from providers.serializers import ExternalSecuritySerializer,\
    CompleteExternalSecuritySerializer
from django.http.response import Http404, HttpResponseBadRequest, JsonResponse
from gso_finance_2.tracks_utility import get_track_content

class ExternalSecurityViewSet(viewsets.ModelViewSet):
    queryset = ExternalSecurity.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CompleteExternalSecuritySerializer
        return ExternalSecuritySerializer
    
class ExternalSecuritySearch(generics.ListAPIView):
    
    serializer_class = ExternalSecuritySerializer
    
    def get_queryset(self):
        provider_code = self.kwargs['provider_code']
        provider_identifier = self.kwargs['provider_identifier']
        queryset = ExternalSecurity.objects.filter(provider__provider_code=provider_code, provider_identifier=provider_identifier)
        
        return queryset
    
class ExternalSecurityUnmapped(generics.ListAPIView):

    serializer_class = CompleteExternalSecuritySerializer
    
    def get_queryset(self):
        queryset = ExternalSecurity.objects.filter(associated__isnull=True).order_by('name')
        
        return queryset
    
def external_securities_history(request, external_security_id):
    try:
        working_security = ExternalSecurity.objects.get(id=external_security_id)
    except:
        raise Http404("External security with id [" + external_security_id + "] is not available.")
    if working_security.provider.provider_code not in [None, '']:
        track_data = get_track_content(working_security.provider.provider_code, working_security.provider_identifier, 'price')
        return JsonResponse(track_data,safe=False)
    else:
        return HttpResponseBadRequest()
    