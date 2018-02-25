'''
Created on 2 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from portfolio.models import Portfolio, Account, Operation,\
    FinancialOperationType, OperationStatus, MoneyAccountChain,\
    AccountType
import logging
from common.models import Currency
    
LOGGER = logging.getLogger(__name__)

class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ('id', 'identifier', 'default_name', 'quick_access')

class CompletePortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ('id', 'identifier', 'name', 'description', 'currency', 'active', 'inception_date',
                  'closing_date', 'management_company', 'relationship_manager', 'bank',
                  'provider', 'last_update', 'last_computation', 'logo', 'accounts',
                  'additional_information', 'additional_description', 'current_aum_local', 'current_aum_mgmt')
        depth = 3
        
class PortfolioSerializer(serializers.ModelSerializer):
    
    current_accounts = []
    
    class Meta:
        model = Portfolio
        fields = ('id', 'identifier', 'name', 'description', 'currency', 'active', 'inception_date',
                  'closing_date', 'management_company', 'relationship_manager', 'bank',
                  'provider', 'last_update', 'last_computation', 'logo', 'accounts',
                  'additional_information', 'additional_description', 'current_aum_local', 'current_aum_mgmt')
    def is_valid(self, raise_exception=False):
        self.current_accounts = []
        wrk_accounts = self.initial_data.pop('accounts') if 'accounts' in self.initial_data else []
        to_validate = []
        for account in wrk_accounts:
            if isinstance(account, int):
                self.current_accounts.append(account)
            else:
                to_validate.append(account['id'])
        if len(to_validate)>0:
            self.initial_data['accounts'] = to_validate
        for field_key in ['currency', 'management_company', 'relationship_manager', 'bank', 'provider', 'account']:
            if field_key in self.initial_data and isinstance(self.initial_data[field_key], dict):
                self.initial_data[field_key] = self.initial_data[field_key]['id']
            
        return serializers.ModelSerializer.is_valid(self, raise_exception=raise_exception)
    
    def save(self, **kwargs):
        portfolio = serializers.ModelSerializer.save(self, **kwargs)
        for account_currency in self.current_accounts:
            acc_currency = Currency.objects.get(id=account_currency)
            new_account = Account()
            new_account.identifier = 'C/C ' + acc_currency.identifier
            new_account.name = 'C/C ' + acc_currency.identifier
            new_account.currency = acc_currency
            new_account.bank = portfolio.bank
            new_account.inception_date = portfolio.inception_date
            new_account.closing_date = None
            new_account.type = AccountType.objects.get(identifier='ACC_CURRENT')
            new_account.save()
            portfolio.accounts.add(new_account)
        return portfolio
        
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'identifier', 'name', 'currency', 'active', 'inception_date', 'closing_date', 'bank',
                  'current_amount_local', 'current_amount_portfolio', 'last_update', 'last_computation',
                  'include_valuation', 'additional_information', 'additional_description')
        depth = 2
        
class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ('id', 'identifier', 'name', 'description', 'spot_rate', 'amount', 'amount_portfolio',
                  'amount_management', 'operation_date', 'value_date', 'status', 'operation_type',
                  'source', 'target', 'security', 'quantity', 'price', 'associated_operation',
                  'additional_information', 'additional_description')
        depth = 2
        
class FinancialOperationTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FinancialOperationType
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class OperationStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationStatus
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class MoneyAccountChainSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyAccountChain
        fields = ('id', 'account', 'operation', 'valid_until', 'operation_amount', 'account_amount')
        depth = 3
