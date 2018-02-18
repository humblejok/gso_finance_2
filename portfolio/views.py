from rest_framework import viewsets, generics
from portfolio.models import Portfolio, Account, Operation, MoneyAccountChain,\
    SecurityAccountChain, AccountType, FinancialOperationType, OperationStatus
from portfolio.serializers import AccountSerializer,  OperationSerializer, MoneyAccountChainSerializer, SecurityAccountChainSerializer,\
    CompletePortfolioSerializer, PortfolioSerializer, AccountTypeSerializer,\
    FinancialOperationTypeSerializer, OperationStatusSerializer
from django.db.models import Q

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

class PortfolioHoldings(generics.ListAPIView):
    serializer_class = SecurityAccountChainSerializer
    
    def get_queryset(self):
        portfolio_id = self.kwargs['portfolio_id']
        account_ids = Portfolio.objects.get(id=portfolio_id).accounts.filter(type__identifier='ACC_SECURITY').order_by('name').values_list('id', flat=True)
        # TODO: Fix this shit
        relevant_ids = []
        for account_id in account_ids:
            result = SecurityAccountChain.objects.filter(account__id=account_id).order_by('-id')
            if result.exists():
                relevant_ids.append(result[0].id)
        return SecurityAccountChain.objects.filter(id__in=relevant_ids)
    
    
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