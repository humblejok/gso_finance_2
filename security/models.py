from django.db import models
from common.models import Currency, Company
from django.contrib.postgres.fields.hstore import HStoreField
from django.contrib.postgres.fields.jsonb import JSONField
import csv
from gso_finance_2.settings import RESOURCES_DIR
import os

from datetime import datetime as dt
from json import loads
from gso_finance_2.tracks_utility import set_track_content

##############################################################
#                  ENVIRONMENT MODELS                        #
##############################################################

class SecurityType(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=True)


##############################################################
#                     SECURITY MODELS                        #
##############################################################
class Security(models.Model):
    identifier = models.CharField(max_length=128, null=False, blank=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    currency = models.ForeignKey(Currency, related_name='security_currency_rel')
    active = models.BooleanField(default=True)
    inception_date = models.DateField(null=False)
    closing_date = models.DateField(null=True)
    management_company = models.ForeignKey(Company, related_name='security_mgmt_company_rel', blank=True, null=True)
    bank = models.ForeignKey(Company, related_name='security_bank_company_rel', blank=True, null=True)
    provider = models.ForeignKey(Company, related_name='security_provider_company_rel', blank=True, null=True)
    provider_identifier = models.CharField(max_length=128, null=True, blank=True)
    
    last_update = models.DateField(null=True)
    
    type = models.ForeignKey(SecurityType, related_name='security_type_rel')
    
    logo = models.CharField(max_length=256, blank=True, null=True)
    
    additional_information = HStoreField(null=True, blank=True)
    additional_description = JSONField(null=True, blank=True)
    
    def get_price_divisor(self):
        if self.additional_information!=None and 'price_divisor' in self.additional_information:
            return self.additional_information['price_divisor']
        if self.type.identifier=='SECTYP_BOND':
            return 100.0
        return 1.0
        
    
    @staticmethod
    def import_from_csv(clean=False, skip_save=False, tracks=False, file_name='securities.csv'):
        if clean:
            Security.objects.all().delete()
        import_reader = csv.reader(open(os.path.join(RESOURCES_DIR,file_name), encoding='utf-8'), delimiter=';')
        header = None
        print("Securities - First pass")
        for row in import_reader:
            if len(row)==0:
                continue
            if header==None:
                header = row
                continue
            print("Creating:" + row[1])
            print(row)
            new_security = Security()
            index = -1
            for column in header:
                index = index + 1
                if column in ['management_company', 'bank', 'provider', 'active'] or row[index]=='':
                    continue
                print(column + ":" + row[index])
                if column in ['inception_date', 'closing_date'] and row[index]!='':
                    print("DATE:" + row[index])
                    setattr(new_security, column, dt.strptime(row[index], '%Y-%m-%d'))
                elif column=='currency' and row[index]!='':
                    setattr(new_security, column, Currency.objects.get(identifier=row[index]))
                elif column=='additional_description':
                    setattr(new_security, column, loads(row[index]))
                elif column=='type':
                    setattr(new_security, column, SecurityType.objects.get(identifier=row[index]))
                else:
                    setattr(new_security, column, row[index].encode('utf-8') if row[index]!='' else None)
            if not skip_save:
                new_security.save()
            for column in ['currency', 'management_company', 'bank', 'provider']:
                index = header.index(column)
                if column=='active':
                    setattr(new_security, column, row[index]=='True')
                elif column=='management_company' and row[index]!='':
                    setattr(new_security, column, Company.objects.get(default_name=row[index]))
                elif column=='bank' and row[index]!='':
                    setattr(new_security, column, Company.objects.get(default_name=row[index]))
                elif column=='provider' and row[index]!='':
                    setattr(new_security, column, Company.objects.get(default_name=row[index]))                    
            if not skip_save:
                new_security.save()
            if tracks:
                key = new_security.additional_description['aliases']['FINALE']['value']
                with open(os.path.join(RESOURCES_DIR, key + '.track')) as track_data:
                    data = loads(track_data.read())
                print(new_security.provider_identifier)
                set_track_content(new_security.provider.provider_code, new_security.provider_identifier, 'price', data, False)
                          
