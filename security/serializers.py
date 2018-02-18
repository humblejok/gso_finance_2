'''
Created on 11 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from security.models import SecurityType, Security

class SecurityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityType
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class SecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = ('id', 'identifier', 'name', 'currency', 'active', 'inception_date', 'closing_date', 'bank',
                  'management_company', 'provider', 'last_update', 'provider_identifier',
                  'type', 'logo', 'additional_description')
        depth = 2