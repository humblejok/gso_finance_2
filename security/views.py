from rest_framework import viewsets, generics
from security.models import SecurityType, Security
from security.serializers import SecurityTypeSerializer, SecuritySerializer
from django.http.response import Http404, JsonResponse, HttpResponseBadRequest
from gso_finance_2.tracks_utility import get_track_content
from django.db.models import Q
import base64
from gso_finance_2.utility import base64urldecode

class SecurityTypeViewSet(viewsets.ModelViewSet):
    queryset = SecurityType.objects.all().order_by('identifier')
    serializer_class = SecurityTypeSerializer
    
class QuickSecurityTypeViewSet(viewsets.ModelViewSet):
    queryset = SecurityType.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = SecurityTypeSerializer
    
class SecurityViewSet(viewsets.ModelViewSet):
    queryset = Security.objects.all().order_by('identifier')
    serializer_class = SecuritySerializer
    
class SecuritiesSearch(generics.ListAPIView):
    serializer_class = SecuritySerializer
    
    def get_queryset(self):
        search_filter = self.kwargs['search_filter']
        search_filter = base64.b64decode(base64urldecode(search_filter))
        print(search_filter)
        queryset = Security.objects.filter(Q(name__icontains=search_filter)
                                           | Q(identifier__icontains=search_filter)
                                           | Q(provider_identifier__icontains=search_filter)
                                           | Q(additional_description__icontains=search_filter)).order_by('name')
        
        return queryset


# TODO: GET ONLY
def securities_history(request, security_id):
    try:
        working_security = Security.objects.get(id=security_id)
    except:
        raise Http404("Security with id [" + security_id + "] is not available.")
    if working_security.provider.provider_code not in [None, '']:
        track_data = get_track_content(working_security.provider.provider_code, working_security.provider_identifier, 'price')
        return JsonResponse(track_data,safe=False)
    else:
        return HttpResponseBadRequest()
    