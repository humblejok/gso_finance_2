'''
Created on 2 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from common.models import Currency, Company

class CurrencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Currency
        fields = ('identifier', 'default_name', 'quick_access')
        
class CompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        fields = ('default_name', 'creation_date', 'base_currency', 'active', 'logo', 'is_provider', 'provider_code')