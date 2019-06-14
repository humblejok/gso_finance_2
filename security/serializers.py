'''
Created on 11 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from security.models import SecurityType, Security
from common.models import Currency, Company

class SecurityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityType
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class CompleteSecuritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Security
        fields = ('id', 'identifier', 'name', 'currency', 'active', 'inception_date', 'closing_date', 'bank',
                  'management_company', 'provider', 'last_update', 'provider_identifier',
                  'type', 'logo', 'additional_description')
        depth = 3
        
        
class SecuritySerializer(serializers.ModelSerializer):
    
    additional_information = {}
    additional_description = {}
    
    class Meta:
        model = Security
        fields = ('id', 'identifier', 'name', 'currency', 'active', 'inception_date', 'closing_date', 'bank',
                  'management_company', 'provider', 'last_update', 'provider_identifier',
                  'type', 'logo', 'additional_description')
    def is_valid(self, raise_exception=False):
        for field_key in ['currency', 'provider', 'type', 'management_company', 'bank']:
            if field_key in self.initial_data and isinstance(self.initial_data[field_key], dict):
                self.initial_data[field_key] = self.initial_data[field_key]['id']
            elif field_key in self.initial_data and isinstance(self.initial_data[field_key], str):
                if field_key=='currency':
                    self.initial_data[field_key] = Currency.objects.get(identifier=self.initial_data[field_key]).id
                elif field_key=='provider':
                    self.initial_data[field_key] = Company.objects.get(provider_code=self.initial_data[field_key]).id
                elif field_key=='type':
                    self.initial_data[field_key] = SecurityType.objects.get(identifier=self.initial_data[field_key]).id
                elif field_key in ['management_company', 'bank']:
                    self.initial_data[field_key] = Company.objects.get(default_name=self.initial_data[field_key]).id
        for field_key in ['closing_date', 'inception_date', 'last_update']:
            if field_key in self.initial_data and self.initial_data[field_key]!=None and len(self.initial_data[field_key])>10:
                self.initial_data[field_key] = self.initial_data[field_key][0:10]
        for field_key in ['additional_information', 'additional_description']:
            if field_key in self.initial_data and self.initial_data[field_key]!=None:
                setattr(self, field_key, self.initial_data[field_key])
                self.initial_data[field_key] = None
        return serializers.ModelSerializer.is_valid(self, raise_exception=raise_exception)
    
    def save(self, **kwargs):
        security = serializers.ModelSerializer.save(self, **kwargs)
        security.additional_information = self.additional_information
        security.additional_description = self.additional_description
        security.save()
        return security
    
    def update(self, instance, validated_data):
        if instance.additional_description!=None:
            instance.additional_description.update(self.additional_description)
        if instance.additional_information!=None:
            instance.additional_information.update(self.additional_information)
        security = serializers.ModelSerializer.update(self, instance, validated_data)
        security.additional_information = self.additional_information
        security.additional_description = self.additional_description
        security.save()