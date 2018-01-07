'''
Created on 2 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from portfolio.models import Portfolio, Account

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ('id', 'identifier', 'name', 'description', 'currency', 'active', 'inception_date',
                  'closing_date', 'management_company', 'relationship_manager', 'bank',
                  'provider', 'last_update', 'last_computation', 'logo', 'accounts',
                  'additional_information', 'additional_description', 'current_aum_local', 'current_aum_mgmt')
        depth = 2
        
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'identifier', 'name', 'currency', 'active', 'inception_date', 'closing_date', 'bank',
                  'current_amount_local', 'current_amount_portfolio', 'last_update', 'last_computation',
                  'include_valuation', 'additional_information', 'additional_description')
        depth = 1