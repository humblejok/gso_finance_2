from rest_framework import viewsets, generics
from providers.models import ExternalSecurity
from providers.serializers import ExternalSecuritySerializer

class ExternalSecurityViewSet(viewsets.ModelViewSet):
    queryset = ExternalSecurity.objects.all()
    serializer_class = ExternalSecuritySerializer
    
class ExternalSecuritySearch(generics.ListAPIView):
    
    serializer_class = ExternalSecuritySerializer
    
    def get_queryset(self):
        provider_code = self.kwargs['provider_code']
        provider_identifier = self.kwargs['provider_identifier']
        queryset = ExternalSecurity.objects.filter(provider__provider_code=provider_code, provider_identifier=provider_identifier)
        
        return queryset