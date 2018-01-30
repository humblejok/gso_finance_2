from rest_framework import viewsets
from security.models import SecurityType
from security.serializers import SecurityTypeSerializer

class SecurityTypeViewSet(viewsets.ModelViewSet):
    queryset = SecurityType.objects.all().order_by('identifier')
    serializer_class = SecurityTypeSerializer
    
class QuickSecurityTypeViewSet(viewsets.ModelViewSet):
    queryset = SecurityType.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = SecurityTypeSerializer