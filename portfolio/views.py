from rest_framework import viewsets, generics
from portfolio.models import Portfolio, Account, Operation, MoneyAccountChain,\
    AccountType, FinancialOperationType, OperationStatus
from portfolio.serializers import AccountSerializer,  OperationSerializer, MoneyAccountChainSerializer,\
    CompletePortfolioSerializer, PortfolioSerializer, AccountTypeSerializer,\
    FinancialOperationTypeSerializer, OperationStatusSerializer
from django.db.models import Q
from django.http.response import Http404, JsonResponse
from gso_finance_2.tracks_utility import get_track_content

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all().order_by('name')
    
    def get_serializer_class(self):
        print("Action=" + self.action)
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
    
    
def portfolios_history(request, portfolio_id, data_type):
    try:
        working_portfolio = Portfolio.objects.get(id=portfolio_id)
    except:
        raise Http404("Portfolio with id [" + portfolio_id + "] is not available.")
    track_data = get_track_content('finance', working_portfolio.id, data_type)
    return JsonResponse(track_data,safe=False)
