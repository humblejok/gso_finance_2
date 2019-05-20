from django.db import models
from common.models import Currency, Company, Person
import os
import csv
from gso_finance_2.settings import RESOURCES_DIR
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.fields.hstore import HStoreField
from security.models import Security
from json import loads
from datetime import datetime as dt
from django.db.models import Q
import logging
from _decimal import Decimal
from gso_finance_2.utility import my_class_import
from portfolio.computations import security_accounts


LOGGER = logging.getLogger(__name__)

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
    currency = models.ForeignKey(Currency, related_name='account_currency_rel', on_delete=models.DO_NOTHING)
    active = models.BooleanField(default=True)
    bank = models.ForeignKey(Company, related_name='account_bank_company_rel', null=True, blank=True, on_delete=models.DO_NOTHING)
    current_amount_local = models.DecimalField(default=0.0, max_digits=26, decimal_places=12)
    current_amount_portfolio = models.DecimalField(default=0.0, max_digits=26, decimal_places=12)
    include_valuation = models.BooleanField(default=True)
    inception_date = models.DateField(null=False)
    closing_date = models.DateField(null=True)
    last_update = models.DateTimeField(null=True)
    last_computation = models.DateTimeField(null=True)

    type = models.ForeignKey(AccountType, related_name='account_type_rel', null=True, blank=True, on_delete=models.DO_NOTHING)

    additional_information = HStoreField(null=True, blank=True)
    additional_description = JSONField(null=True, blank=True)

    def create_initialization(self, application_date, amount, spot_portfolio=0.0, spot_management=0.0):
        init_operation = Operation()
        init_operation.identifier = 'INIT_' + self.identifier
        init_operation.name = 'Initialize account'
        init_operation.description = 'Created automatically'
        init_operation.spot_rate = 1.0
        init_operation.amount = amount
        init_operation.amount_portfolio = amount * spot_portfolio # TODO: Correct
        init_operation.amount_management = amount * spot_management # TODO: Correct
        init_operation.operation_date = application_date
        init_operation.value_date = application_date
        init_operation.status = OperationStatus.objects.get(identifier='OPE_STATUS_EXECUTED')
        init_operation.additional_information = None
        init_operation.additional_description = None
        init_operation.operation_type = FinancialOperationType.objects.get(identifier='OPE_TYPE_CONTRIBUTION' if amount>0.0 else 'OPE_TYPE_WITHDRAWAL')
        init_operation.source = None if amount>0.0 else self
        init_operation.target = self if amount>0.0 else None
        init_operation.security = None
        init_operation.quantity = 0.0
        init_operation.price = 0.0
        init_operation.save()
        return init_operation


    @staticmethod
    def instanciate_from_dict(data):
        new_instance = Account()
        for key in data:
            if key=='model':
                continue
            if key=='currency':
                setattr(new_instance, key, Currency.objects.get(identifier=data[key]))
            elif key=='type':
                setattr(new_instance, key, AccountType.objects.get(identifier=data[key]))
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
    source = models.ForeignKey(Company, related_name='valuation_source', blank=True, null=True, on_delete=models.DO_NOTHING)
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
    identifier = models.CharField(max_length=256, null=False, blank=False)
    name = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    spot_rate = models.FloatField(default=1.0)
    amount = models.FloatField()
    amount_portfolio = models.FloatField(blank=True, null=True)
    amount_management = models.FloatField(blank=True, null=True)
    operation_date = models.DateField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey(OperationStatus, related_name='operation_status_rel', on_delete=models.DO_NOTHING)

    additional_information = HStoreField(null=True, blank=True)
    additional_description = JSONField(null=True, blank=True)

    operation_type = models.ForeignKey(FinancialOperationType, related_name='investmemt_operation_type_rel', blank=True, null=True, on_delete=models.DO_NOTHING)
    source = models.ForeignKey(Account, related_name='operation_source', blank=True, null=True, on_delete=models.DO_NOTHING)
    target = models.ForeignKey(Account, related_name='operation_target', blank=True, null=True, on_delete=models.DO_NOTHING)
    security = models.ForeignKey(Security, related_name='operation_security', blank=True, null=True, on_delete=models.DO_NOTHING)
    quantity = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)

    associated_operation = models.ForeignKey('Operation', related_name='operation_parent', null=True, on_delete=models.CASCADE)

    @staticmethod
    def create_from_v1(portfolio, operation_dict):
        LOGGER.info('Trying to create operation [' + operation_dict['name'] + ']')
        operation = Operation()
        operation.identifier = operation_dict['short_name']
        operation.name = operation_dict['name']
        operation.description = operation_dict['short_description']
        operation.spot_rate = operation_dict['spot']
        operation.amount = operation_dict['amount']
        operation.amount_portfolio = 0.0
        operation.amount_management = 0.0
        operation.operation_date = operation_dict['operation_date']
        operation.value_date = operation_dict['value_date']
        operation.status = OperationStatus.objects.get(identifier=operation_dict['operation_status']['identifier'])
        operation.additional_information = {'valuation_spots_up_to_date': False, 'to_be_linked': None, 'import_id': operation_dict['id']}
        operation.operation_type = FinancialOperationType.objects.get(identifier=operation_dict['operation_type']['identifier'])
        operation.quantity = operation_dict['quantity']
        operation.price = operation_dict['price']

        if operation_dict['associated_operation']!=None:
            operation.additional_information['to_be_linked'] = operation_dict['associated_operation']['id']

        if operation_dict['source']!=None:
            LOGGER.info("Looking for " + operation_dict['source']['name'])
            operation.source = portfolio.accounts.get(Q(name=operation_dict['source']['name']) | Q(name=operation_dict['source']['short_name']))
        else:
            operation.source = None
        if operation_dict['target']!=None:
            if operation_dict['target']['type']['identifier']=='CONT_ACCOUNT':
                LOGGER.info("Looking for " + operation_dict['target']['name'])
                operation.target = portfolio.accounts.get(Q(name=operation_dict['target']['name']) |Q(name=operation_dict['target']['short_name']) )
                operation.security = None
            else:
                LOGGER.info("Looking for " + operation_dict['target']['name'] + "/" + str(operation_dict['target']['id']))
                operation.target = portfolio.accounts.get(name=operation_dict['repository']['name']) if operation_dict['repository']!=None else None
                operation.security = Security.objects.get(additional_description__aliases__FINALE__value=str(operation_dict['target']['id']))
        else:
            operation.target = None
            operation.security = None
        operation.save()
        LOGGER.info('\tCreated')


class Portfolio(models.Model):
    identifier = models.CharField(max_length=128, null=False, blank=False)
    name = models.CharField(max_length=128, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    currency = models.ForeignKey(Currency, related_name='portfolio_currency_rel', on_delete=models.DO_NOTHING)
    active = models.BooleanField(default=True)
    inception_date = models.DateField(null=False)
    closing_date = models.DateField(null=True)
    management_company = models.ForeignKey(Company, related_name='portfolio_mgmt_company_rel', null=True, blank=True, on_delete=models.DO_NOTHING)
    relationship_manager = models.ForeignKey(Person, related_name='portfolio_rm_person_rel', null=True, blank=True, on_delete=models.DO_NOTHING)
    bank = models.ForeignKey(Company, related_name='portfolio_bank_company_rel', null=True, blank=True, on_delete=models.DO_NOTHING)
    provider = models.ForeignKey(Company, related_name='portfolio_provider_company_rel', null=True, blank=True, on_delete=models.DO_NOTHING)
    last_update = models.DateField(null=True)
    last_computation = models.DateField(null=True)
    logo = models.CharField(max_length=256, blank=True, null=True)

    current_aum_local = models.FloatField(default=0.0)
    current_aum_mgmt = models.FloatField(default=0.0)
    
    previous_day = models.FloatField(default=0.0)
    week_to_date = models.FloatField(default=0.0)
    month_to_date = models.FloatField(default=0.0)
    quarter_to_date = models.FloatField(default=0.0)
    year_to_date = models.FloatField(default=0.0)
    
    accounts = models.ManyToManyField(Account, blank=True, related_name='portfolio_accounts_rel')

    additional_information = HStoreField(null=True, blank=True)
    additional_description = JSONField(null=True, blank=True)
    
    def create_security_position(self, security, quantity, buy_price, as_of):
        new_op = Operation()
        new_op.identifier = ('BUY_' if quantity>0 else 'SELL_') + security.identifier
        new_op.name = ('BUY ' if quantity>0 else 'SELL ') + security.identifier
        new_op.description = 'Initialization of a security position'
        new_op.spot_rate = 1.0
        new_op.amount = quantity * buy_price / security.get_price_divisor()
        new_op.operation_date = as_of
        new_op.value_date = as_of
        new_op.status = OperationStatus.objects.get(identifier='OPE_STATUS_EXECUTED')
        new_op.operation_type = FinancialOperationType.objects.get(identifier='OPE_TYPE_BUY_FOP' if quantity>0 else 'OPE_TYPE_SELL_FOP')
        new_op.source = None
        new_op.target = None
        new_op.security = security
        new_op.target = self.get_or_create_security_account(security.currency.identifier)
        new_op.quantity = quantity
        new_op.price = buy_price
        new_op.save()
        return new_op
        
    def create_account_from_external(self, e_account):
        new_account = Account()
        new_account.active = True
        new_account.name = e_account.name
        new_account.identifier = e_account.provider_identifier
        new_account.currency = e_account.currency
        new_account.bank = self.bank
        new_account.current_amount_local = 0.0
        new_account.current_amount_portfolio = 0.0 # TODO: Complete
        new_account.include_valuation = True
        new_account.inception_date = self.inception_date
        new_account.closing_date = self.closing_date
        new_account.last_computation = dt.now()
        new_account.last_update = dt.now()
        new_account.type = e_account.type 
        new_account.additional_description = {'aliases': {self.provider.provider_code: e_account.provider_identifier }}
        new_account.save()
        self.accounts.add(new_account)
        return new_account
    
    def get_or_create_security_account(self, currency_code):
        try:
            account = self.accounts.get(type__identifier='ACC_SECURITY', currency__identifier=currency_code)
        except:
            account = Account()
            account.name = "Security " + currency_code
            account.active = True
            account.additional_description = {}
            account.additional_information = {}
            account.bank = Company.objects.get(id=self.bank.id)
            account.closing_date = self.closing_date
            account.currency = Currency.objects.get(identifier=currency_code)
            account.current_amount_local = 0.0
            account.current_amount_portfolio = 0.0
            account.identifier = "Security " + currency_code
            account.inception_date = self.inception_date
            account.include_valuation = True
            account.last_computation = dt.now()
            account.last_update = dt.now()
            account.type = AccountType.objects.get(identifier='ACC_SECURITY')
            account.save()
            self.accounts.add(account)
        return account
    
    def import_simple(self, path_to_file, initial_amounts, application_date):
        accounts_ids = [account.id for account in self.accounts.all()]
        Operation.objects.filter(Q(source__id__in=accounts_ids) | Q(target__id__in=accounts_ids)).delete()
        EXTERNAL_SECURITY = my_class_import('providers.models.ExternalSecurity')
        operations = []
        with open(path_to_file, 'r') as ops_file:
            operations = loads(ops_file.read())
        for operation in operations:
            print(operation)
            new_op = Operation()
            new_op.identifier = 'BUY ' + operation['position']
            new_op.name = 'BUY ' + operation['position']
            new_op.description = 'Simple import'
            new_op.spot_rate = 0.0
            new_op.amount = operation['quantity'] * operation['price']
            new_op.operation_date = application_date
            new_op.value_date = application_date
            new_op.status = OperationStatus.objects.get(identifier='OPE_STATUS_EXECUTED')
            new_op.operation_type = FinancialOperationType.objects.get(identifier='OPE_TYPE_BUY_FOP')
            new_op.source = None
            new_op.security = EXTERNAL_SECURITY.objects.get(provider__provider_code=operation['source'], provider_identifier=operation['position']).associated
            new_op.quantity = operation['quantity']
            new_op.price = operation['price']
            print("Security currency:" + new_op.security.currency.identifier)
            if new_op.security==None:
                print("Security " + operation['position'] + " is not associated!")
            else:
                if not self.accounts.filter(type__identifier='ACC_SECURITY', currency__identifier=new_op.security.currency.identifier).exists():
                    account = Account()
                    account.identifier = 'Securities ' + new_op.security.currency.identifier
                    account.name = 'Securities ' + new_op.security.currency.identifier
                    account.currency = new_op.security.currency
                    account.active = True
                    account.bank = self.bank
                    account.inception_date = self.inception_date
                    account.closing_date = None
                    account.last_update = None
                    account.last_computation = None
                    account.type = AccountType.objects.get(identifier='ACC_SECURITY')
                    account.save()
                    self.accounts.add(account)
                else:
                    account = self.accounts.get(type__identifier='ACC_SECURITY', currency__identifier=new_op.security.currency.identifier)
                new_op.target = account                
                
                new_op.save()
        for amount in initial_amounts:
            if not self.accounts.filter(type__identifier='ACC_CURRENT', currency__identifier=amount['currency']).exists():
                account = Account()
                account.identifier = 'C/C ' + new_op.security.currency.identifier
                account.name = 'C/C ' + new_op.security.currency.identifier
                account.currency = new_op.security.currency
                account.active = True
                account.bank = self.bank
                account.inception_date = self.inception_date
                account.closing_date = None
                account.last_update = None
                account.last_computation = None
                account.type = AccountType.objects.get(identifier='ACC_CURRENT')
                account.save()
                self.accounts.add(account)
            else:
                account = self.accounts.get(type__identifier='ACC_CURRENT', currency__identifier=amount['currency'])
            new_op = Operation()
            new_op.identifier = 'Initial contribution ' + amount['currency']
            new_op.name = 'Contribution ' + amount['currency']
            new_op.description = 'Simple import'
            new_op.spot_rate = 1.0
            new_op.amount = amount['amount']
            new_op.operation_date = application_date
            new_op.value_date = application_date
            new_op.status = OperationStatus.objects.get(identifier='OPE_STATUS_EXECUTED')
            new_op.operation_type = FinancialOperationType.objects.get(identifier='OPE_TYPE_CONTRIBUTION')
            new_op.source = None
            new_op.target = account
            new_op.security = None
            new_op.quantity = 0.0
            new_op.price = 0.0
            new_op.save()
        for account in self.accounts.all():
            if account.type.identifier!='ACC_SECURITY':
                print(account.id)
                MoneyAccountChain.build_chain(account)
            else:
                print(account.id)
                security_accounts.build_chain(account)
                portfolio = account.portfolio_accounts_rel.all()[0]
                security_accounts.compute_valuation(portfolio, account)

    def import_v1_transactions(self):
        accounts_ids = [account.id for account in self.accounts.all()]
        Operation.objects.filter(Q(source__id__in=accounts_ids) | Q(target__id__in=accounts_ids)).delete()
        with open(os.path.join(RESOURCES_DIR,self.name), 'r') as transactions_file:
            data = transactions_file.read()
        data = loads(data)
        for transaction in data:
            Operation.create_from_v1(self, transaction)
        for account in self.accounts.all():
            if account.type.identifier!='ACC_SECURITY':
                MoneyAccountChain.build_chain(account)

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
    reference_portfolio = models.ForeignKey(Portfolio, related_name='conso_portfolio_reference_rel', null=False, on_delete=models.DO_NOTHING)
    included_portfolio = models.ManyToManyField(Portfolio, related_name='conso_included_portfolio_rel', blank=True)

class MoneyAccountChain(models.Model):
    account = models.ForeignKey(Account, related_name='account_chain', on_delete=models.DO_NOTHING)
    operation = models.ForeignKey(Operation, related_name='account_operation_chain', on_delete=models.DO_NOTHING)
    valid_until = models.DateField(null=True, blank=True)
    account_amount = models.DecimalField(max_digits=26, decimal_places=12)
    operation_amount = models.DecimalField(max_digits=26, decimal_places=12)

    @staticmethod
    def build_chain(account):
        all_operations = Operation.objects.filter(Q(source__id=account.id) | Q(target__id=account.id)).distinct().order_by('value_date', 'id')
        MoneyAccountChain.objects.filter(account__id=account.id).delete()
        amount = Decimal(0.0)
        previous_chain = None
        for operation in all_operations:
            print('Operation:' + operation.name + ' === ' + str(operation.amount))
            operation_amount = Decimal(operation.amount)
            
            if operation.target!=None and operation.security==None:
                print(operation.amount)
                if operation.target.id==account.id:
                    operation_amount = operation_amount * Decimal(operation.spot_rate)
                else:
                    operation_amount = operation_amount * Decimal(-1.0)
            if operation.security!=None:
                operation_amount = operation_amount * Decimal(operation.spot_rate) * (Decimal(-1.0) if operation.operation_type.identifier in ['OPE_TYPE_BUY', 'OPE_TYPE_BUY_FOP'] else Decimal(1.0))
            if operation.target==None and operation.source!=None:
                operation_amount = operation_amount * Decimal(operation.spot_rate)
            amount = amount + (operation_amount if operation.status.identifier!='OPE_CANCELLED' and not operation.operation_type.identifier in ['OPE_TYPE_BUY_FOP', 'OPE_TYPE_SELL_FOP'] else Decimal(0.0))
            new_chain = MoneyAccountChain()
            new_chain.account = account
            new_chain.operation = operation
            new_chain.valid_until = None
            new_chain.account_amount = amount
            new_chain.operation_amount = operation_amount
            new_chain.save()
            print("Amount:" + str(amount))
            if previous_chain!=None:
                previous_chain.valid_until = operation.value_date
                previous_chain.save()
            previous_chain = new_chain
        account.current_amount_local = amount
        account.last_update = dt.today()
        account.save()
