from django.db import models
from common.models import Company, Currency
from security.models import SecurityType, Security

import logging

from portfolio.models import Portfolio, AccountType, Account, Operation

LOGGER = logging.getLogger(__name__)

               
class ExternalSecurity(models.Model):
    name = models.CharField(max_length=128)
    type = models.ForeignKey(SecurityType, related_name='external_security_type_rel', blank=True, null=True)
    currency = models.ForeignKey(Currency, related_name='external_security_currency_rel', blank=True, null=True)
    provider = models.ForeignKey(Company, related_name='external_security_providing_company', blank=True, null=True)
    provider_identifier = models.CharField(max_length=128, blank=True, null=True)
    associated = models.ForeignKey(Security, null=True, blank=True, related_name='external_security_link')
    potential_matches = models.ManyToManyField(Security, blank=True, related_name='external_security_potential_link')
    
class ExternalAccount(models.Model):
    name = models.CharField(max_length=128)
    type = models.ForeignKey(AccountType, related_name='external_account_type_rel', blank=True, null=True)
    currency = models.ForeignKey(Currency, related_name='external_account_currency_rel', blank=True, null=True)
    provider = models.ForeignKey(Company, related_name='external_account_providing_company', blank=True, null=True)
    provider_identifier = models.CharField(max_length=128, blank=True, null=True)
    associated = models.ForeignKey(Account, null=True, blank=True, related_name='external_account_link')
    potential_matches = models.ManyToManyField(Account, blank=True, related_name='external_account_potential_link')
    
class PortfolioSecurityHolding(models.Model):
    external_security = models.ForeignKey(ExternalSecurity, related_name='external_security_holding')
    external_price = models.FloatField(default=0.0)
    external_quantity = models.FloatField(default=0.0)
    internal_security = models.ForeignKey(Security, related_name='internal_security_holding', null=True, blank=True)
    internal_price = models.FloatField(default=0.0, null=True, blank=True)
    internal_quantity = models.FloatField(default=0.0, null=True, blank=True)
    
class PortfolioAccountHolding(models.Model):
    external_account = models.ForeignKey(ExternalAccount, related_name='external_account_holding')
    external_quantity = models.FloatField(default=0.0)
    internal_account= models.ForeignKey(Account, related_name='internal_account_holding', null=True, blank=True)
    internal_quantity = models.FloatField(default=0.0, null=True, blank=True)

class ExternalPortfolioHoldings(models.Model):
    provider = models.ForeignKey(Company, related_name='portfolio_holdings_provider', null=True, blank=True)
    portfolio = models.ForeignKey(Portfolio, related_name='portfolio_holdings_portfolio')
    application_date = models.DateField()
    security_holdings = models.ManyToManyField(PortfolioSecurityHolding, related_name='portfolio_holdings_securities')
    account_holdings = models.ManyToManyField(PortfolioAccountHolding, related_name='portfolio_holdings_accounts')
    
class ExternalTransaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='external_transaction_portfolio')
    provider = models.ForeignKey(Company, related_name='external_transaction_provider', null=True, blank=True)
    provider_identifier = models.CharField(max_length=128, blank=True, null=True)
    internal_operation = models.ForeignKey(Operation, related_name='external_transaction_operation')
    external_source = models.ForeignKey(ExternalAccount, related_name='external_transaction_source', null=True, blank=True)
    external_target = models.ForeignKey(ExternalAccount, related_name='external_transaction_target', null=True, blank=True)
    external_security = models.ForeignKey(ExternalSecurity, related_name='external_transaction_security', null=True, blank=True)
    is_valid = models.BooleanField(default=False)
    is_imported = models.BooleanField(default=False)