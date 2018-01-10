'''
Created on 2 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from providers.models import ExternalSecurity

class ExternalSecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalSecurity
        fields = ('id', 'name', 'type', 'currency', 'provider', 'provider_identifier', 'provider_data')
        depth = 1
