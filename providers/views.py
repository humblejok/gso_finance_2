from rest_framework import viewsets, generics
from providers.models import ExternalSecurity, ExternalAccount,\
    PortfolioSecurityHolding, PortfolioAccountHolding, ExternalPortfolioHoldings
from providers.serializers import ExternalSecuritySerializer,\
    ExternalAccountSerializer, PortfolioSecurityHoldingSerializer,\
    PortfolioAccountHoldingSerializer, ExternalPortfolioHoldingsSerializer
from django.http.response import Http404, HttpResponseBadRequest, JsonResponse,\
    HttpResponse
from gso_finance_2.tracks_utility import get_track_content
from portfolio.models import Account
from datetime import datetime as dt
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

# TODO: EVERYTHING -> Check usage and migrate to EAMCOM?


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
    
class ExternalSecurityUnmapped(generics.ListAPIView):

    serializer_class = ExternalSecuritySerializer
    
    def get_queryset(self):
        queryset = ExternalSecurity.objects.filter(associated__isnull=True).order_by('name')
        
        return queryset

@require_http_methods(["GET"])
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

class ExternalAccountViewSet(viewsets.ModelViewSet):
    queryset = ExternalAccount.objects.all()
    serializer_class = ExternalAccountSerializer
    
class PortfolioSecurityHoldingViewSet(viewsets.ModelViewSet):
    queryset = PortfolioSecurityHolding.objects.all()
    serializer_class = PortfolioSecurityHoldingSerializer
    
class PortfolioAccountHoldingViewSet(viewsets.ModelViewSet):
    queryset = PortfolioAccountHolding.objects.all()
    serializer_class = PortfolioAccountHoldingSerializer
    
class ExternalPortfolioHoldingsViewSet(viewsets.ModelViewSet):
    queryset = ExternalPortfolioHoldings.objects.all()
    serializer_class = ExternalPortfolioHoldingsSerializer

@csrf_exempt
@require_http_methods(["POST"])
def create_account_from(request, account_holding_id, holdings_id):
    try:
        holdings = ExternalPortfolioHoldings.objects.get(id=holdings_id)
        account_holding = PortfolioAccountHolding.objects.get(id=account_holding_id)
    except (ExternalPortfolioHoldings.DoesNotExist, PortfolioAccountHolding.DoesNotExist) as e:
        return Http404('Either the external portfolio information are not present anymore or the external account information.')
    new_account = Account()
    new_account.active = True
    new_account.name = account_holding.external_account.name
    new_account.identifier = account_holding.external_account.provider_identifier
    new_account.currency = account_holding.external_account.currency
    new_account.bank = holdings.portfolio.bank
    new_account.current_amount_local = account_holding.external_quantity
    new_account.current_amount_portfolio = 0.0 # TODO: Complete
    new_account.include_valuation = True
    new_account.inception_date = holdings.portfolio.inception_date
    new_account.closing_date = holdings.portfolio.closing_date
    new_account.last_computation = dt.now()
    new_account.last_update = dt.now()
    new_account.type = account_holding.external_account.type 
    new_account.additional_description = {'aliases': {holdings.provider.provider_code: account_holding.external_account.provider_identifier }}
    new_account.save()
    holdings.portfolio.accounts.add(new_account)
    account_holding.internal_account = new_account
    account_holding.internal_quantity = account_holding.external_quantity
    account_holding.save()
    
    return HttpResponse(status_code=201)
        
@csrf_exempt
@require_http_methods(["POST"])
def assign_account_to(request, account_holding_id, account_id):
    try:
        account = Account.objects.get(id=account_id)
        account_holding = PortfolioAccountHolding.objects.get(id=account_holding_id)
    except (ExternalPortfolioHoldings.DoesNotExist, PortfolioAccountHolding.DoesNotExist) as e:
        return Http404('Either the internal account information are not present anymore or the external account information.')        
    account.identifier = account_holding.external_account.provider_identifier
    if account.additional_description==None:
        account.additional_description = {}
    if 'aliases' not in account.additional_description:
        account.additional_description['aliases'] = {} 
    account.additional_description['aliases'][account_holding.provider.provider_code] = account_holding.external_account.provider_identifier
    account.save/()
    account_holding.internal_account = account
    account_holding.internal_quantity = account.current_amount_local
    account_holding.save()
    return HttpResponse(status_code=204)
        