'''
Created on 11 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from security.models import SecurityType

class SecurityTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SecurityType
        fields = ('id', 'identifier', 'default_name', 'quick_access')