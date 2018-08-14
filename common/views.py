from django.shortcuts import render
from rest_framework import viewsets, generics
from common.models import Currency, Company, Country, VisibilityLevel,\
    AddressType, PhoneType, MailType, Person
from common.serializers import CurrencySerializer, CompleteCompanySerializer,\
    CountrySerializer, VisibilityLevelSerializer, AddressTypeSerializer,\
    PhoneTypeSerializer, MailTypeSerializer, CompanySerializer,\
    CompletePersonSerializer, PersonSerializer
import base64
from gso_finance_2.utility import base64urldecode
from django.db.models import Q

def index(request):
    return render(request, 'index.html', {})

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all().order_by('default_name')
    serializer_class = CurrencySerializer
    
class QuickCurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.filter(quick_access=True).order_by('default_name')
    serializer_class = CurrencySerializer
    
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all().order_by('identifier')
    serializer_class = CountrySerializer
    
class QuickCountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = CountrySerializer
    
class VisibilityLevelViewSet(viewsets.ModelViewSet):
    queryset = VisibilityLevel.objects.all().order_by('identifier')
    serializer_class = VisibilityLevelSerializer
    
class QuickVisibilityLevelViewSet(viewsets.ModelViewSet):
    queryset = VisibilityLevel.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = VisibilityLevelSerializer
    
class AddressTypeViewSet(viewsets.ModelViewSet):
    queryset = AddressType.objects.all().order_by('identifier')
    serializer_class = AddressTypeSerializer
    
class QuickAddressTypeViewSet(viewsets.ModelViewSet):
    queryset = AddressType.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = AddressTypeSerializer
    
class PhoneTypeViewSet(viewsets.ModelViewSet):
    queryset = PhoneType.objects.all().order_by('identifier')
    serializer_class = PhoneTypeSerializer
    
class QuickPhoneTypeViewSet(viewsets.ModelViewSet):
    queryset = PhoneType.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = PhoneTypeSerializer
    
class MailTypeViewSet(viewsets.ModelViewSet):
    queryset = MailType.objects.all().order_by('identifier')
    serializer_class = MailTypeSerializer
    
class QuickMailTypeViewSet(viewsets.ModelViewSet):
    queryset = MailType.objects.filter(quick_access=True).order_by('identifier')
    serializer_class = MailTypeSerializer
    
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('default_name')
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CompleteCompanySerializer
        return CompanySerializer
    
class ProviderSearch(generics.ListAPIView):
    serializer_class = CompleteCompanySerializer
   
    def get_queryset(self):
        provider_code = self.kwargs['provider_code']
        queryset = Company.objects.filter(is_provider=True, provider_code=provider_code)
        
        return queryset
    
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by('default_name')
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CompletePersonSerializer
        return PersonSerializer
    
class CompaniesSearch(generics.ListAPIView):
    serializer_class = CompleteCompanySerializer
    
    def get_queryset(self):
        search_filter = self.kwargs['search_filter']
        search_filter = base64.b64decode(base64urldecode(search_filter))
        print(search_filter)
        queryset = Company.objects.filter(Q(default_name__icontains=search_filter)
                                           | Q(provider_code__icontains=search_filter)).order_by('name')
        
        return queryset