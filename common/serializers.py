'''
Created on 2 janv. 2018

@author: sdejo
'''
from rest_framework import serializers
from common.models import Currency, Company, Country, VisibilityLevel,\
    AddressType, PhoneType, MailType, CompanyMemberRole, CompanySubsidiaryRole,\
    Address, Email, Phone, Person, CompanyMember, CompanySubsidiary

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class VisibilityLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisibilityLevel
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class AddressTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressType
        fields = ('id', 'identifier', 'default_name', 'quick_access')

class PhoneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneType
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class MailTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailType
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class CompanyMemberRoleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyMemberRole
        fields = ('id', 'identifier', 'default_name', 'quick_access')
        
class CompanySubsidiaryRoleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySubsidiaryRole
        fields = ('id', 'identifier', 'default_name', 'quick_access')

        
class CompleteCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'default_name', 'creation_date', 'base_currency', 'addresses', 'emails', 'phones', 'members', 'subsidiaries', 'active', 'logo', 'is_provider', 'provider_code')
        depth = 2

class CompanySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Company
        fields = ('id', 'default_name', 'creation_date', 'base_currency', 'addresses', 'emails', 'phones', 'members', 'subsidiaries', 'active', 'logo', 'is_provider', 'provider_code')
    def is_valid(self, raise_exception=False):
        for field_key in ['base_currency', 'addresses', 'emails', 'phones', 'members', 'subsidiaries']:
            if field_key in self.initial_data and isinstance(self.initial_data[field_key], dict):
                self.initial_data[field_key] = self.initial_data[field_key]['id']
        for field_key in ['creation_date']:
            if field_key in self.initial_data and self.initial_data[field_key]!=None and len(self.initial_data[field_key])>10:
                self.initial_data[field_key] = self.initial_data[field_key][0:10]
            
        return serializers.ModelSerializer.is_valid(self, raise_exception=raise_exception)
    
    def save(self, **kwargs):
        company = serializers.ModelSerializer.save(self, **kwargs)
        return company

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'address_type', 'line_1', 'line_2', 'zip_code', 'city', 'country')
        depth = 1
        
class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ('id', 'address_type', 'email_address')
        depth = 1
        
class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('id', 'line_type', 'phone_number')
        depth = 1
    
class CompletePersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'default_name', 'first_name', 'last_name', 'birth_date', 'addresses', 'emails', 'phones', 'active', 'picture')
        depth = 2
        
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'default_name', 'first_name', 'last_name', 'birth_date', 'addresses', 'emails', 'phones', 'active', 'picture')
    def is_valid(self, raise_exception=False):
        for field_key in ['addresses', 'emails', 'phones']:
            if field_key in self.initial_data and isinstance(self.initial_data[field_key], dict):
                self.initial_data[field_key] = self.initial_data[field_key]['id']
        for field_key in ['birth_date']:
            if field_key in self.initial_data and self.initial_data[field_key]!=None and len(self.initial_data[field_key])>10:
                self.initial_data[field_key] = self.initial_data[field_key][0:10]
            
        return serializers.ModelSerializer.is_valid(self, raise_exception=raise_exception)
    
    def save(self, **kwargs):
        company = serializers.ModelSerializer.save(self, **kwargs)
        return company

class CompanyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyMember
        fields = ('id', 'person', 'role')
        depth = 2
        
class CompanySubsidiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySubsidiary
        fields = ('id', 'company', 'role')
        depth = 2