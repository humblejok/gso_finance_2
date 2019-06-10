'''
Created on 10 juin 2019

@author: humblejok
'''
from portfolio.models import Portfolio, Account, AccountType
from django.http.response import Http404, HttpResponse
from json import loads
from common.models import Currency, Company
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime as dt


# TODO: Use REST Framework
@csrf_exempt
@require_http_methods(["POST"])
def accounts_create_or_update(request, portfolio_identifier):
    try:
        portfolio = Portfolio.objects.get(identifier=portfolio_identifier)
    except Portfolio.DoesNotExist:
        return Http404('Portfolio with this identifier doesn''t exist!')
    request_data = loads(request.body)
    for account_info in request_data:
        try:
            account = Account.objects.get(identifier=account_info['identifier'])
        except Account.DoesNotExist:
            account = Account()
            account.identifier = account_info['identifier']
        account.name = account_info['name']
        try:
            account.currency = Currency.objects.get(identifier=account_info['currency'])
        except Currency.DoesNotExist:
            return Http404("Currency does not exists")
        account.active = account_info['active'] if 'active' in account_info else True
        try:
            account.bank = portfolio.bank if not 'bank' in account_info else Company.objects.get(identifier=account_info['bank'])
        except Company.DoesNotExist:
            return Http404("Company does not exists")
        account.include_valuation = True if not 'include_valuation' in account_info else account_info['include_valuation']
        if 'inception_date' in account_info:
            account.inception_date = account_info['inception_date']
        if 'closing_date' in account_info:
            account.closing_date = account_info['closing_date']
        account.last_update = dt.now()
        account.type = AccountType.objects.get(identifier=account_info['type'])
        account.save()
        if not portfolio.accounts.filter(id=account.id):
            portfolio.accounts.add(account)
    return HttpResponse(status=201)