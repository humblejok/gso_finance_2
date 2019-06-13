'''
Created on 04 June 2019

@author: sdejo
'''
from django.core.management.base import BaseCommand
from django.db.models import Q

from security.models import Security, SecurityType
from common.models import Currency, Company


class Command(BaseCommand):
    help = 'Create spot security'
    
    def add_arguments(self, parser):
        parser.add_argument('from_currency', type=str)
        parser.add_argument('to_currency', type=str)
        parser.add_argument('provider_code', type=str)

    def handle(self, *args, **options):
        source_currency = options['from_currency']
        target_currency = options['to_currency']
        provider_code = options['provider_code']
        security = Security.objects.filter(provider_identifier='{0}{1} Curncy'.format(source_currency, target_currency), provider__provider_code=provider_code)
        if not security.exists():
            print('Spot security does not exist, creating...')
            security = Security()
            security.identifier = '{0}{1} X-RATE'.format(source_currency, target_currency)
            security.name = '{0}{1} Spot Exchange Rate'.format(source_currency, target_currency)
            security.active = True
            security.inception_date = '2000-01-01'
            provider = Company.objects.get(provider_code=provider_code)
            security.additional_description =   {
                                                    'aliases': {
                                                        provider.provider_code: {
                                                            'value': '{0}{1} Curncy'.format(source_currency, target_currency),
                                                            'additional': ''
                                                        }
                                                    }
                                                }
            security.currency = Currency.objects.get(identifier=target_currency)
            security.provider = provider
            security.type = SecurityType.objects.get(identifier='SECTYP_CURRENCY')
            security.provider_identifier = '{0}{1} Curncy'.format(source_currency, target_currency)
            security.save()
            print('Spot security created!')
        else:
            print('Spot security already exists')