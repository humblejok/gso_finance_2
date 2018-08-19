'''
Created on 2 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from providers.models import ExternalSecurity, ExternalAccount,\
    PortfolioSecurityHolding, PortfolioAccountHolding, ExternalPortfolioHoldings,\
    ExternalTransaction

class ExternalSecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalSecurity
        fields = ('id', 'name', 'type', 'currency', 'provider', 'provider_identifier', 'associated', 'potential_matches')
        depth = 3
        
class ExternalAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalAccount
        fields = ('id', 'name', 'type', 'currency', 'provider', 'provider_identifier', 'associated', 'potential_matches')
        depth = 3
        
class PortfolioSecurityHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioSecurityHolding
        fields = ('id', 'external_security', 'external_price', 'external_quantity', 'internal_security', 'internal_price', 'internal_quantity')
        depth = 3
        
class PortfolioAccountHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioAccountHolding
        fields = ('id', 'external_account', 'external_quantity', 'internal_account', 'internal_quantity')
        depth = 3
        
class ExternalPortfolioHoldingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalPortfolioHoldings
        fields = ('id', 'provider', 'application_date', 'security_holdings', 'account_holdings')
        depth = 3
        
class ExternalTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalTransaction
        fields = ('id', 'portfolio', 'provider', 'provider_identifier', 'internal_operation',
                  'external_source', 'external_target', 'external_security', 'is_valid', 'is_imported')
        depth = 3