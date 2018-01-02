from django.db import models
from django.contrib.postgres.fields.hstore import HStoreField
from datetime import datetime as dt
from common.models import Company, Currency
from django.contrib.postgres.fields.jsonb import JSONField
from gso_finance_2.settings import PROVIDERS_DIR, PROVIDERS_COMPLETED_DIR_NAME
from os.path import isdir
from security.models import SecurityType

import csv
import os
import logging

import shutil


LOGGER = logging.getLogger(__name__)


class VP_PositionType(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)
    
class VP_PositionTypeMap(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=False)

class VP_Position(models.Model):
    application_date = models.DateField()
    source_file = models.CharField(max_length=128)
    treated = models.BooleanField(default=False)
    treated_date = models.DateTimeField(null=True, blank=True)
    comment = JSONField()
    data = HStoreField()
    
    @staticmethod
    def populate_one(file_path):
        position_reader = csv.reader(open(file_path), delimiter=';')
        header = None
        file_name = os.path.basename(file_path)
        VP_Position.objects.filter(source_file=file_name).delete()
        application_date = dt.strptime(file_name[4:12], '%Y%m%d')
        for row in position_reader:
            if header==None:
                header = row
                continue
            loaded_data = {}
            index = 0
            for column in header:
                loaded_data[column] = row[index]
                index = index + 1
            new_position = VP_Position()
            new_position.application_date = application_date
            new_position.source_file = file_name
            new_position.treated = False
            new_position.data = loaded_data
            new_position.comment = {'completed': False, 'mapped_to_model': None, 'mapped_to_id': None}
            new_position.save()
            
    @staticmethod
    def populate_all():
        vp_bank = Company.objects.get(default_name='VP Bank')
        if vp_bank.provider_code in [None, '', 'None']:
            vp_bank.provider_code = 'vpbank'
            vp_bank.save()
        source_path = os.path.join(PROVIDERS_DIR, vp_bank.provider_code)
        all_files = os.listdir(source_path)
        csvs = [f for f in all_files if f.endswith('.csv')]
        for element in csvs:
            LOGGER.info("Working on " + element)
            source_file = os.path.join(source_path, element)
            if not isdir(source_file) and element.startswith('POS_'):
                VP_Position.populate_one(source_file)
                shutil.move(source_file, os.path.join(PROVIDERS_DIR, vp_bank.provider_code, PROVIDERS_COMPLETED_DIR_NAME))
                
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