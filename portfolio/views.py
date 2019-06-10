from rest_framework import viewsets, generics
from portfolio.models import Portfolio, Account, Operation, MoneyAccountChain, \
    AccountType, FinancialOperationType, OperationStatus
from portfolio.serializers import AccountSerializer, OperationSerializer, MoneyAccountChainSerializer, \
    CompletePortfolioSerializer, PortfolioSerializer, AccountTypeSerializer, \
    FinancialOperationTypeSerializer, OperationStatusSerializer
from django.db.models import Q
from django.http.response import Http404, JsonResponse, HttpResponse,\
    HttpResponseServerError
from gso_finance_2.tracks_utility import get_track_content, get_multi_last,\
    set_track_content
from portfolio.computations import portfolios as pf_computer
from security.models import Security
from security.serializers import CompleteSecuritySerializer
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from json import loads
from eamcom.utility import import_positions
from providers.models import ExternalAccount, ExternalSecurity,\
    ExternalTransaction
from providers.serializers import ExternalTransactionSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all().order_by('name')
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CompletePortfolioSerializer
        return PortfolioSerializer
    
class OperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer

class AccountOperations(generics.ListAPIView):
    serializer_class = MoneyAccountChainSerializer

    def get_queryset(self):
        account_id = self.kwargs['account_id']
        queryset = MoneyAccountChain.objects.filter(Q(account__id=account_id)).order_by('-id')
        return queryset

    
class AccountTypeViewSet(viewsets.ModelViewSet):
    queryset = AccountType.objects.all().order_by('identifier')
    serializer_class = AccountTypeSerializer
    
class QuickAccountTypeViewSet(viewsets.ModelViewSet):
    queryset = AccountType.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = AccountTypeSerializer
    
class FinancialOperationTypeViewSet(viewsets.ModelViewSet):
    queryset = FinancialOperationType.objects.all().order_by('identifier')
    serializer_class = FinancialOperationTypeSerializer
    
class QuickFinancialOperationTypeViewSet(viewsets.ModelViewSet):
    queryset = FinancialOperationType.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = FinancialOperationTypeSerializer
    
class OperationStatusViewSet(viewsets.ModelViewSet):
    queryset = OperationStatus.objects.all().order_by('identifier')
    serializer_class = OperationStatusSerializer
    
class QuickOperationStatusViewSet(viewsets.ModelViewSet):
    queryset = OperationStatus.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = OperationStatusSerializer
    
def portfolio_holdings(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    all_data = []
    for account in portfolio.accounts.filter(type__identifier='ACC_SECURITY'):
        all_quantity = get_multi_last('finance', account.id, 'positions')
        if all_quantity:
            qt_key = next(iter(all_quantity))
            all_valued = get_multi_last('finance', account.id, 'valued_holdings')
            all_local_w = get_multi_last('finance', account.id, 'holdings_weights_local')
            all_portfolio_w = get_multi_last('finance', account.id, 'holdings_weights_portfolio')
            all_buy_prices = get_multi_last('finance', account.id, 'buy_prices')
            for security_id in all_quantity[qt_key]:
                if all_quantity[qt_key][security_id] != 0.0:
                    entry = {}
                    security = Security.objects.get(id=security_id)
                    serializer = CompleteSecuritySerializer(security)
                    entry['security'] = serializer.data
                    entry['quantity'] = all_quantity[qt_key][security_id]
                    entry['value'] = all_valued[next(iter(all_valued))][security_id]
                    entry['weight_local'] = all_local_w[next(iter(all_local_w))][security_id]
                    entry['weight_portfolio'] = all_portfolio_w[next(iter(all_portfolio_w))][security_id]
                    entry['buy_price'] = all_buy_prices[next(iter(all_buy_prices))][security_id]
                    entry['current_price'] = entry['value'] / entry['quantity'] * security.get_price_divisor()
                    entry['gross_performance_local'] = ((entry['current_price'] / entry['buy_price']) - 1.0) if entry['buy_price'] != 0.0 else 0.0
                    entry['holding_account_id'] = account.id
                    all_data.append(entry)
    return JsonResponse(sorted(all_data, key=lambda entry: entry['security']['currency']['identifier'] + entry['security']['name']), safe=False)

def portfolio_security_operations(request, portfolio_id, account_id, security_id):
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id)
    except:
        return Http404("Portfolio does not exists")
    try:
        account = portfolio.accounts.get(id=account_id)
    except:
        return Http404("Account does not exists")
    operations = Operation.objects.filter(target__id=account.id, security__id=security_id,
                                          operation_type__identifier__in=['OPE_TYPE_SWITCH', 'OPE_TYPE_BUY', 'OPE_TYPE_BUY_FOP', 'OPE_TYPE_SELL_FOP', 'OPE_TYPE_SELL']
                                          ).order_by('-value_date')
    serializer = OperationSerializer(operations, many=True)
    return JsonResponse(serializer.data, safe=False)
                        

def portfolios_history(request, portfolio_id, data_type):
    try:
        working_portfolio = Portfolio.objects.get(id=portfolio_id)
    except:
        raise Http404("Portfolio with id [" + portfolio_id + "] is not available.")
    track_data = get_track_content('finance', working_portfolio.id, data_type)
    return JsonResponse(track_data, safe=False)

def portfolio_compute(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    pf_computer.compute_accounts(portfolio)
    pf_computer.compute_valuation(portfolio)
    pf_computer.update_accounts(portfolio)
    pf_computer.update_portfolio_model(portfolio)
    return HttpResponse(status=200)

@csrf_exempt
@require_http_methods(["POST"])
def portfolio_initialize(request, portfolio_identifier, as_of):
    try:
        portfolio = Portfolio.objects.get(identifier=portfolio_identifier)
    except Portfolio.DoesNotExist:
        return Http404('Portfolio with this identifier doesn''t exist!')
    request_data = loads(request.body)
    status = import_positions(request_data)
    if status:
        forwards = {}
        for entry in request_data:
            if entry['asset_class'].startswith('ACC_'):
                e_account = ExternalAccount.objects.get(provider=portfolio.provider, provider_identifier=entry['identifier'])
                if e_account.associated==None:
                    account = portfolio.create_account_from_external(e_account)
                    e_account.associated = account
                    e_account.save()
                else:
                    account = Account.objects.get(id=e_account.associated.id)
                if entry['quantity']!=0.0 and entry['asset_class']!='ACC_FORWARD':
                    account.create_initialization(as_of, entry['quantity'])
                elif entry['asset_class']=='ACC_FORWARD':
                    key = entry['identifier'][-4:]
                    if key not in forwards:
                        forwards[key] = []
                    forwards[key].append(entry)
            else:
                print(entry['identifier'])
                e_security = ExternalSecurity.objects.get(provider=portfolio.provider, provider_identifier=entry['identifier'])
                portfolio.create_security_position(e_security.associated, entry['quantity'], entry['price'], as_of)
        for forward_key in forwards:
            forward = forwards[forward_key]
            if forward[0]['quantity']!=0.0 and forward[1]['quantity']!=0.0:
                source_index = 0 if forward[0]['quantity']<0.0 else 1
                target_index = 1 if forward[0]['quantity']<0.0 else 0
                from_account = Account.objects.get(identifier=forward[source_index]['identifier'])
                to_account = Account.objects.get(identifier=forward[target_index]['identifier'])
                Operation.create_spot('INIT_' + forward[0]['identifier'], from_account, to_account, abs(forward[source_index]['quantity']), abs(forward[target_index]['quantity'] / forward[source_index]['quantity']), as_of, as_of)
    else:
        return HttpResponseServerError('Positions could not be treated.')
    return HttpResponse(status=201)

@csrf_exempt
@require_http_methods(["POST"])
def portfolio_import_history(request, portfolio_identifier):
    try:
        portfolio = Portfolio.objects.get(identifier=portfolio_identifier)
    except Portfolio.DoesNotExist:
        return Http404('Portfolio with this identifier doesn''t exist!')
    request_data = loads(request.body)
    track_content = []
    for entry in request_data:
        track_content.append({'date': entry['date'], 'value': entry['performance']})
    set_track_content('finance', portfolio.id, 'performance_past', track_content, True)
    return HttpResponse(status=201)

@require_http_methods(["GET"])
def portfolios_setup(request):
    # TODO: Use configuration file
    pf_setup = {
        'additional_information': [
            {'name': 'PROVIDER_ONLY', 'default_value': False, 'default_label': 'Provider only', 'default_description': 'Displayed data are not computed by FinanCE but extracted from the provider.', 'type': 'boolean'},
            {'name': 'FUND_OR_ASSIMILATED', 'default_value': False, 'default_label': 'Is this portfolio a fund or assimilated?', 'default_description': 'This will enable advanced fees computations but also subscription and redemption in the associated security will be reflected in the portfolio.', 'type': 'boolean'}
            ]
        }
    return JsonResponse(pf_setup, safe=True)


@require_http_methods(["GET"])
def portfolio_transactions_external_pending(request, portfolio_id):
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id)
    except:
        return Http404("Portfolio does not exists")
    transactions = ExternalTransaction.objects.filter(portfolio__id=portfolio.id, is_imported=False).order_by('internal_operation__value_date')
    serializer = ExternalTransactionSerializer(transactions, many=True)
    return JsonResponse(serializer.data, safe=False)