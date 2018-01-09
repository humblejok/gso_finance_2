from django.db import models
from django.contrib.postgres.fields.hstore import HStoreField
from common.models import Company, Currency
from security.models import SecurityType, Security

import logging

from portfolio.models import Portfolio


LOGGER = logging.getLogger(__name__)

               
class ExternalSecurity(models.Model):
    name = models.CharField(max_length=128)
    type = models.ForeignKey(SecurityType, related_name='external_security_type_rel', blank=True, null=True)
    currency = models.ForeignKey(Currency, related_name='external_security_currency_rel', blank=True, null=True)
    provider = models.ForeignKey(Company, related_name='external_security_providing_company', blank=True, null=True)
    provider_identifier = models.CharField(max_length=128, blank=True, null=True)
    source_id = models.IntegerField(null=True, blank=True)
    provider_data = HStoreField(null=True, blank=True)
    
    
class ExternalSecurityPrice(models.Model):
    security = models.ForeignKey(ExternalSecurity, related_name='external_security_pricing')
    pricing_history = HStoreField(null=True, blank=True)
    
class PortfolioHolding(models.Model):
    external_security = models.ForeignKey(ExternalSecurity, related_name='external_holding')
    external_price = models.FloatField(default=0.0)
    external_quantity = models.FloatField(default=0.0)
    internal_security = models.ForeignKey(Security, related_name='internal_holding')
    internal_price = models.FloatField(default=0.0)
    internal_quantity = models.FloatField(default=0.0)

class ExternalPortfolioHoldings(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='portfolio_holdings')
    application_date = models.DateField()
    holdings = models.ManyToManyField(PortfolioHolding, related_name='portfolio_holdings_consolidation')
    
    