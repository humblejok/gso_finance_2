'''
Created on 2 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from portfolio.models import Portfolio, Account

class PortfolioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Portfolio
        fields = ('identifier', 'name', 'description', 'currency', 'active', 'inception_date', 'closing_date')
        
class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ('identifier', 'name', 'currency', 'active', 'inception_date', 'closing_date', 'bank',
                  'current_amount_local', 'current_amount_portfolio', 'last_update', 'last_computation',
                  'include_valuation')