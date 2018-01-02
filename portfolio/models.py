from django.db import models
from common.models import Currency, Company, Person
import os
import csv
from gso_finance_2.settings import RESOURCES_DIR
from gso_finance_2.utility import my_class_import
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.fields.hstore import HStoreField
from security.models import Security
from json import loads
from datetime import datetime as dt

##############################################################
#                  ENVIRONMENT MODELS                        #
##############################################################

class AccountType(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=True)
    
class FinancialOperationType(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=True)
    
class ForexOperationType(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=True)
    
class InvestmentOperationType(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=True)

class OperationStatus(models.Model):
    identifier = models.CharField(max_length=32)
    default_name = models.CharField(max_length=128)
    quick_access = models.BooleanField(default=True)

##############################################################
#                     PORTOLIO MODELS                        #
##############################################################

class Account(models.Model):
    identifier = models.CharField(max_length=32, null=False, blank=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    currency = models.ForeignKey(Currency, related_name='account_currency_rel')
    active = models.BooleanField(default=True)
    bank = models.ForeignKey(Company, related_name='account_bank_company_rel', null=True, blank=True)
    current_amount_local = models.FloatField(default=0.0)
    current_amount_portfolio = models.FloatField(default=0.0)
    include_valuation = models.BooleanField(default=True)
    inception_date = models.DateField(null=False)
    closing_date = models.DateField(null=True)
    last_update = models.DateField(null=True)
    last_computation = models.DateField(null=True)
    
    additional_information = HStoreField(null=True, blank=True)
    additional_description = JSONField(null=True, blank=True)
    
    @staticmethod
    def instanciate_from_dict(data):
        new_instance = Account()
        for key in data:
            if key=='model':
                continue
            if key=='currency':
                setattr(new_instance, key, Currency.objects.get(identifier=data[key]))
            elif key=='bank':
                if data[key]!='':
                    setattr(new_instance, key, Company.objects.get(default_name=data[key]))
            elif key in ['inception_date', 'closing_date', 'last_update', 'last_computation']:
                if data[key]!='':
                    setattr(new_instance, key, dt.strptime(data[key], '%Y-%m-%d'))
            else:
                setattr(new_instance, key, data[key])
        new_instance.save()
        return new_instance
    

class Valuation(models.Model):
    value_date = models.DateField()
    investments_portfolio = models.FloatField()
    investments_management = models.FloatField()
    cash_portfolio = models.FloatField()
    cash_management = models.FloatField()
    total_portfolio = models.FloatField()
    total_management = models.FloatField()
    daily_performance = models.FloatField()
    weekly_performance = models.FloatField()
    monthly_performance = models.FloatField()
    quarterly_performance = models.FloatField()
    semester_performance = models.FloatField()
    yearly_performance = models.FloatField()
    inception_performance = models.FloatField()
    investments_performance = models.FloatField()
    fx_performance = models.FloatField()
    investments_weight = models.FloatField()
    cash_weight = models.FloatField()
    positions = models.ManyToManyField(Security, related_name='valuation_securities_rel', blank=True)
    
    movements_cash = models.FloatField()
    movements_negative_cash = models.FloatField()
    movements_positive_cash = models.FloatField()
    movements_loan_cash = models.FloatField()
    movements_investments = models.FloatField()
    movements_investments_fop = models.FloatField()
    
class Operation(models.Model):
    identifier = models.CharField(max_length=32, null=False, blank=False)
    name = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    spot_rate = models.FloatField(default=1.0)
    amount = models.FloatField()
    amount_portfolio = models.FloatField(blank=True, null=True)
    amount_management = models.FloatField(blank=True, null=True)
    operation_date = models.DateField()
    value_date = models.DateField()
    
    status = models.ForeignKey(OperationStatus, related_name='operation_status_rel')
    
    additional_information = HStoreField(null=True, blank=True)
    additional_description = JSONField()
    

class FinancialOperation(models.Model):
    operation_type = models.ForeignKey(FinancialOperationType, related_name='financial_operation_type_rel')
    source = models.ForeignKey(Account, related_name='financial_operation_source', blank=True, null=True)
    target = models.ForeignKey(Account, related_name='financial_operation_target', blank=True, null=True)

class ForexOperation(models.Model):
    operation_type = models.ForeignKey(ForexOperationType, related_name='forex_operation_type_rel')
    source = models.ForeignKey(Account, related_name='forex_operation_source', blank=True, null=True)
    target = models.ForeignKey(Account, related_name='forex_operation_target', blank=True, null=True)
    
class InvestmentOperation(models.Model):
    operation_type = models.ForeignKey(InvestmentOperationType, related_name='investmemt_operation_type_rel')
    source = models.ForeignKey(Account, related_name='investmemt_operation_source', blank=True, null=True)
    target = models.ForeignKey(Security, related_name='investmemt_operation_target', blank=True, null=True)
    quantity = models.FloatField()
    price = models.FloatField()

class Portfolio(models.Model):
    identifier = models.CharField(max_length=128, null=False, blank=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    currency = models.ForeignKey(Currency, related_name='portfolio_currency_rel')
    active = models.BooleanField(default=True)
    inception_date = models.DateField(null=False)
    closing_date = models.DateField(null=True)
    management_company = models.ForeignKey(Company, related_name='portfolio_mgmt_company_rel', null=True, blank=True)
    relationship_manager = models.ForeignKey(Person, related_name='portfolio_rm_person_rel', null=True, blank=True)
    bank = models.ForeignKey(Company, related_name='portfolio_bank_company_rel', null=True, blank=True)
    provider = models.ForeignKey(Company, related_name='portfolio_provider_company_rel', null=True, blank=True)
    last_update = models.DateField(null=True)
    last_computation = models.DateField(null=True)
    logo = models.CharField(max_length=256, blank=True, null=True)
    
    current_aum_local = models.FloatField(default=0.0)
    current_aum_mgmt = models.FloatField(default=0.0)
    
    accounts = models.ManyToManyField(Account, blank=True, related_name='portfolio_accounts_rel')
    
    additional_information = HStoreField(null=True, blank=True)
    additional_description = JSONField(null=True, blank=True)
    
    @staticmethod
    def import_from_csv(clean=False):
        if clean:
            Portfolio.objects.all().delete()
            Account.objects.all().delete()
        import_reader = csv.reader(open(os.path.join(RESOURCES_DIR,'portfolios.csv'), encoding='utf-8'), delimiter=';')
        header = None
        print("Portfolios - First pass")
        for row in import_reader:
            if len(row)==0:
                continue
            if header==None:
                header = row
                continue
            print("Creating:" + row[1])
            print(row)
            new_portfolio = Portfolio()
            index = -1
            for column in header:
                index = index + 1
                if column in ['accounts', 'management_company', 'relationship_manager', 'bank', 'provider', 'active'] or row[index]=='':
                    continue
                print(column + ":" + row[index])
                if column in ['inception_date', 'closing_date'] and row[index]!='':
                    print("DATE:" + row[index])
                    setattr(new_portfolio, column, dt.strptime(row[index], '%Y-%m-%d'))
                elif column=='currency' and row[index]!='':
                    setattr(new_portfolio, column, Currency.objects.get(identifier=row[index]))
                else:
                    setattr(new_portfolio, column, row[index].encode('utf-8') if row[index]!='' else None)
            new_portfolio.save()
            for column in ['currency', 'management_company', 'relationship_manager', 'bank', 'provider']:
                index = header.index(column)
                if column=='active':
                    setattr(new_portfolio, column, row[index]=='True')
                elif column=='management_company' and row[index]!='':
                    setattr(new_portfolio, column, Company.objects.get(default_name=row[index]))
                elif column=='relationship_manager' and row[index]!='':
                    setattr(new_portfolio, column, Person.objects.get(default_name=row[index]))
                elif column=='bank' and row[index]!='':
                    setattr(new_portfolio, column, Company.objects.get(default_name=row[index]))
                elif column=='provider' and row[index]!='':
                    setattr(new_portfolio, column, Company.objects.get(default_name=row[index]))                    
            for column in ['accounts']:
                all_data = loads(row[header.index(column)], encoding='utf-8')
                for data in all_data:
                    working_class = Account
                    getattr(new_portfolio, column).add(working_class.instanciate_from_dict(data))
            new_portfolio.save()

class ConsolidationPortfolio(Portfolio):
    reference_portfolio = models.ForeignKey(Portfolio, related_name='conso_portfolio_reference_rel', null=False)
    included_portfolio = models.ManyToManyField(Portfolio, related_name='conso_included_portfolio_rel', blank=True)
