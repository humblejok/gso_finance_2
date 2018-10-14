from rest_framework import viewsets, generics
from security.models import SecurityType, Security
from security.serializers import SecurityTypeSerializer, SecuritySerializer,\
    CompleteSecuritySerializer
from django.http.response import Http404, JsonResponse, HttpResponseBadRequest,\
    HttpResponseServerError, HttpResponse
from gso_finance_2.tracks_utility import get_track_content, STATISTICS_ENGINE,\
    set_multi_content, set_track_content, compute_track_content
from django.db.models import Q
import base64
from gso_finance_2.utility import base64urldecode
from django.views.decorators.http import require_http_methods
import requests

class SecurityTypeViewSet(viewsets.ModelViewSet):
    queryset = SecurityType.objects.all().order_by('identifier')
    serializer_class = SecurityTypeSerializer
    
class QuickSecurityTypeViewSet(viewsets.ModelViewSet):
    queryset = SecurityType.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = SecurityTypeSerializer
    
class SecurityViewSet(viewsets.ModelViewSet):
    queryset = Security.objects.all().order_by('identifier')
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CompleteSecuritySerializer
        return SecuritySerializer


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


@require_http_methods(["GET"])
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

STATISTICS_FIELDS = ['averageLoss', 'lastReturn', 'yearToDate', 'last3MonthsTotalReturn', 'currentDrawdown', 'annualizedReturn', 'totalReturn', 'averageRateOfReturn', 'averageGain',
                     'percentageOfPositiveMonths', 'annualizedStandardDeviation', 'annualizedLossDeviation', 'skewness', 'kurtosis', 'omega10SinceInception',
                     'omega10Over36Months', 'maximumDrawdown', 'maximumLengthOfDrawdown', 'monthToDate', 'quarterToDate', 'semesterToDate']

@require_http_methods(["GET"])
def securities_statistics(request, security_id):
    try:
        working_security = Security.objects.get(id=security_id)
    except:
        raise Http404("Security with id [" + security_id + "] is not available.")
    if working_security.provider.provider_code not in [None, '']:
        # TODO: Externalize
        HEADERS = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        response = requests.get(STATISTICS_ENGINE + '?source=' + working_security.provider.provider_code.lower() + '&identifier=' + working_security.provider_identifier + '&trackType=price', headers=HEADERS)
        if response.status_code==200:
            data = response.json()
            all_data = {}
            for entry in data:
                wrk_date = entry['applicationDate']
                for STAT in STATISTICS_FIELDS:
                    if STAT not in all_data:
                        all_data[STAT] = []
                    if STAT in entry:
                        all_data[STAT].append({'date': wrk_date, 'value': entry[STAT]})
                set_multi_content('finance', working_security.id, 'last_statistics', {wrk_date: entry}, True)
            for STAT in STATISTICS_FIELDS:
                set_track_content('finance', working_security.id, STAT, all_data[STAT], True)
            prices = get_track_content(working_security.provider.provider_code.lower(), working_security.provider_identifier, 'price', nofill=True)
            set_track_content('finance', working_security.id, 'price', prices, True)
            compute_track_content('finance', working_security.id, 'price', 'pandas_performances', 'performance')
            return JsonResponse(entry, safe=False)
        else:
            return HttpResponseServerError('Statistics engine failed to compute, please contact your administrator.')
    else:
        return HttpResponseBadRequest()

