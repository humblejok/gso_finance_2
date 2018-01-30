from django.shortcuts import render
from rest_framework import viewsets, generics
from common.models import Currency, Company, Country, VisibilityLevel,\
    AddressType, PhoneType, MailType, Person
from common.serializers import CurrencySerializer, CompanySerializer,\
    CountrySerializer, VisibilityLevelSerializer, AddressTypeSerializer,\
    PhoneTypeSerializer, MailTypeSerializer, PersonSerializer

def index(request):
    return render(request, 'index.html', {})

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all().order_by('identifier')
    serializer_class = CurrencySerializer
    
class QuickCurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.filter(quick_access=True).order_by('identifier')
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
    serializer_class = CompanySerializer
    
class ProviderSearch(generics.ListAPIView):
    serializer_class = CompanySerializer
   
    def get_queryset(self):
        provider_code = self.kwargs['provider_code']
        queryset = Company.objects.filter(is_provider=True, provider_code=provider_code)
        
        return queryset
    
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by('default_name')
    serializer_class = PersonSerializer