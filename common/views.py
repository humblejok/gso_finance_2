from django.shortcuts import render
from rest_framework import viewsets
from common.models import Currency, Company
from common.serializers import CurrencySerializer, CompanySerializer

def index(request):
    return render(request, 'index.html', {})

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all().order_by('identifier')
    serializer_class = CurrencySerializer
    
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('default_name')
    serializer_class = CompanySerializer