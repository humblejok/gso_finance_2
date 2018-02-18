'''
Created on 2 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from providers.models import ExternalSecurity

class ExternalSecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalSecurity
        fields = ('id', 'name', 'type', 'currency', 'provider', 'provider_identifier', 'associated')
        
    def is_valid(self, raise_exception=False):
        for field_key in ['type', 'currency', 'provider', 'associated']:
            if isinstance(self.initial_data[field_key], dict):
                self.initial_data[field_key] = self.initial_data[field_key]['id']
            
        return serializers.ModelSerializer.is_valid(self, raise_exception=raise_exception)

class CompleteExternalSecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalSecurity
        fields = ('id', 'name', 'type', 'currency', 'provider', 'provider_identifier', 'associated')
        depth = 3