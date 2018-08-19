'''
Created on 18 août 2018

@author: sdejo
'''
from json import dumps
from common.models import Company, Currency
from providers.models import ExternalSecurity, ExternalAccount,\
    PortfolioSecurityHolding, PortfolioAccountHolding, ExternalTransaction
from security.models import SecurityType, Security
from django.db.models import Q
import logging
from portfolio.models import AccountType, Portfolio, Operation, OperationStatus,\
    FinancialOperationType

LOGGER = logging.getLogger(__name__)


me = Company.objects.get(provider_code='EAMCOM')

# TODO: CACHE THIS
available_provider_codes = Company.objects.filter(is_provider=True).values_list('provider_code', flat=True)

def extract_operation_type(external_type):
    if external_type=='Contribution':
        return FinancialOperationType.objects.get(identifier='OPE_TYPE_CONTRIBUTION')
    if external_type=='Cashier contribution':
        return FinancialOperationType.objects.get(identifier='OPE_TYPE_CASH_CONTRIBUTION')
    if external_type=='Withdrawal':
        return FinancialOperationType.objects.get(identifier='OPE_TYPE_WITHDRAWAL')
    if external_type=='Cashier withdrawal':
        return FinancialOperationType.objects.get(identifier='OPE_TYPE_CASH_WITHDRAWAL')
    return FinancialOperationType.objects.get(identifier='OPE_TYPE_CONTRIBUTION')

def extract_status(external_status):
    if external_status=='Received':
        return OperationStatus.objects.get(identifier='OPE_STATUS_SENT')
    if external_status=='Acknowledged':
        return OperationStatus.objects.get(identifier='OPE_STATUS_ACK')
    if external_status=='Executed':
        return OperationStatus.objects.get(identifier='OPE_STATUS_EXECUTED')
    if external_status=='Cancelled':
        return OperationStatus.objects.get(identifier='OPE_STATUS_CANCELLED')
    return OperationStatus.objects.get(identifier='OPE_STATUS_PENDING')

def extract_security_type(external_type):
    if external_type=='Stock':
        return SecurityType.objects.get(identifier='SECTYP_STOCK')
    if external_type=='Fund':
        return SecurityType.objects.get(identifier='SECTYP_FUND')
    return SecurityType.objects.get(identifier='SECTYP_SECURITY')

def extract_account_type(external_type):
    if external_type=='Cash':
        return AccountType.objects.get(identifier='ACC_CURRENT')
    if external_type=='Loan':
        return AccountType.objects.get(identifier='ACC_LOAN')
    if external_type=='Fiduciary':
        return AccountType.objects.get(identifier='ACC_CAPITAL_CALL')
    return AccountType.objects.get(identifier='ACC_CURRENT_BANK_TECHNICAL')

def extract_potential_securities(data):
    identifiers_query = None
    alias_based_results = []
    for provider_code in available_provider_codes:
        query_string = {'additional_description__aliases__' + provider_code + '__value': data['identifier']}
        if identifiers_query==None:
            identifiers_query = Q(**query_string)
        else:
            identifiers_query |= Q(**query_string)
    if identifiers_query!=None:
        alias_based_results = Security.objects.filter(identifiers_query)
        
    label_based_results = Security.objects.filter(Q(identifier__icontains=data['label'])
                            | Q(identifier__icontains=data['identifier'])
                            | Q(name__icontains=data['label'])
                            | Q(name__icontains=data['identifier'])
                            )
    return list(alias_based_results) + list(label_based_results)

def extract_potential_accounts(portfolio, data, key='identifier'):
    return list(portfolio.accounts.filter(identifier=data[key]))

def create_security_holdings(portfolio_holding, data):
    done = True
    results = []
    for entry in data:
        if entry['asset_class'] in ['Fund', 'Stock', 'Other']:
            try:
                e_security = ExternalSecurity.objects.get(provider=me, provider_identifier=entry['identifier'])
            except:
                LOGGER.error('EAMCOM - Could not find external security for [' + entry['portfolio_id'] + ',' + entry['identifier'] + '] or too many results!')
                done = False
                break
            new_holding = PortfolioSecurityHolding()
            new_holding.external_security = e_security
            new_holding.external_price = entry['price']
            new_holding.external_quantity = entry['quantity']
            new_holding.internal_security = e_security.associated
            # TODO: Complete
            new_holding.internal_price = 0.0
            new_holding.internal_quantity = 0.0
            new_holding.save()
            results.append(new_holding)
    return done, results


def create_account_holdings(portfolio_holding, data):
    done = True
    results = []
    for entry in data:
        if entry['asset_class'] not in ['Fund', 'Stock', 'Other']:
            try:
                e_account = ExternalAccount.objects.get(provider=me, provider_identifier=entry['identifier'])
            except:
                LOGGER.error('EAMCOM - Could not find external account for [' + entry['portfolio_id'] + ',' + entry['identifier'] + '] or too many results!')
                done = False
                break
            new_holding = PortfolioAccountHolding()
            new_holding.external_account = e_account
            new_holding.external_quantity = entry['quantity']
            new_holding.internal_account = e_account.associated
            new_holding.internal_quantity = 0.0 if e_account.associated==None else e_account.associated.current_amount_local
            new_holding.save()
            results.append(new_holding)
    return done, results

def import_positions(data):
    done = True
    for entry in data:
        try:
            portfolio = Portfolio.objects.get(identifier=entry['portfolio_id'])
        except:
            LOGGER.error('EAMCOM - Could not find portfolio with identifier [' + entry['portfolio_id'] + '] or too many results!')
            done = False
            break
        if entry['asset_class'] in ['Fund', 'Stock', 'Other']:
            extract_potential_securities(entry)
            try:
                LOGGER.debug('EAMCOM - Searching existing security - [' + entry['label'] + ',' + entry['identifier'] + ']')
                e_security = ExternalSecurity.objects.get(provider=me, provider_identifier=entry['identifier'], currency__identifier=entry['currency'])
                LOGGER.debug('EAMCOM - Found')
            except ExternalSecurity.DoesNotExist:
                LOGGER.debug('EAMCOM - Not found, creating external security')
                e_security = ExternalSecurity()
            e_security.name = entry['label']
            e_security.type = extract_security_type(entry['asset_class'])
            e_security.currency = Currency.objects.get(identifier=entry['currency'])
            e_security.provider = me
            e_security.provider_identifier = entry['identifier']
            e_security.save()
            LOGGER.debug('EAMCOM - Updating potential matches')
            e_security.potential_matches.clear()
            potentials = extract_potential_securities(entry)
            
            if len(potentials)>0:
                LOGGER.debug('EAMCOM - Has ' + str(len(potentials)) + ' potential matches (possible doublons included)')
                if e_security.associated==None:
                    e_security.associated = potentials[0]
                e_security.potential_matches.add(*potentials)
                e_security.save()
            else:
                LOGGER.debug('EAMCOM - No match found...')
        else:
            try:
                LOGGER.debug('EAMCOM - Searching existing account - [' + entry['label'] + ',' + entry['identifier'] + ']')
                e_account = ExternalAccount.objects.get(provider=me, provider_identifier=entry['identifier'])
                LOGGER.debug('EAMCOM - Found')
            except ExternalAccount.DoesNotExist:
                LOGGER.debug('EAMCOM - Not found, creating external account')
                e_account = ExternalAccount()
            e_account.name = entry['label']
            e_account.type = extract_account_type(entry['asset_class'])
            e_account.currency = Currency.objects.get(identifier=entry['currency'])
            e_account.provider = me
            e_account.provider_identifier = entry['identifier']
            e_account.save()
            LOGGER.debug('EAMCOM - Updating potential matches')
            e_account.potential_matches.clear()
            potentials = extract_potential_accounts(portfolio, entry)
            if len(potentials)>0:
                LOGGER.debug('EAMCOM - Has ' + str(len(potentials)) + ' potential matches (possible doublons included)')
                if e_account.associated==None:
                    e_account.associated = potentials[0]
                e_account.potential_matches.add(*potentials)
                e_account.save()
            else:
                LOGGER.debug('EAMCOM - No match found...')
    return done

def import_cash_operations(data):
    done = True
    results = []
    for entry in data:
        try:
            portfolio = Portfolio.objects.get(identifier=entry['portfolio_id'])
        except:
            LOGGER.error('EAMCOM - Could not find portfolio with identifier [' + entry['portfolio_id'] + '] or too many results!')
            done = False
            break
        try:
            ext_transaction = ExternalTransaction.objects.get(provider=me, portfolio=portfolio, provider_identifier=entry['identifier'])
        except ExternalTransaction.DoesNotExist:
            ext_transaction = ExternalTransaction()
            ext_transaction.portfolio = portfolio
            ext_transaction.provider = me
            ext_transaction.provider_identifier = entry['identifier']
            ext_transaction.internal_operation = Operation()
            ext_transaction.is_imported = False
        f_account = None
        t_account = None
        e_security = None
        if entry['from_account_id'] not in [None, '', 'None']:
            try:
                LOGGER.debug('EAMCOM - Searching existing from account - [' + entry['from_account_id'] + ']')
                f_account = ExternalAccount.objects.get(provider=me, provider_identifier=entry['from_account_id'])
                LOGGER.debug('EAMCOM - Found')
            except ExternalAccount.DoesNotExist:
                LOGGER.debug('EAMCOM - Not found')
        if entry['to_account_id'] not in [None, '', 'None']:
            try:
                LOGGER.debug('EAMCOM - Searching existing to account - [' + entry['to_account_id'] + ']')
                t_account = ExternalAccount.objects.get(provider=me, provider_identifier=entry['to_account_id'])
                LOGGER.debug('EAMCOM - Found')
            except ExternalAccount.DoesNotExist:
                LOGGER.debug('EAMCOM - Not found')
        ext_transaction.is_valid = (t_account!=None and t_account.associated!=None) or (f_account!=None and f_account.associated!=None)
        ext_transaction.external_security = e_security
        ext_transaction.external_source = f_account
        ext_transaction.external_target = t_account
        LOGGER.debug('EAMCOM - Filling internal operation fields')
        ext_transaction.internal_operation.identifier = entry['identifier']
        ext_transaction.internal_operation.name = entry['label']
        ext_transaction.internal_operation.description = entry['label']
        ext_transaction.internal_operation.spot_rate = 1.0
        ext_transaction.internal_operation.amount = float(entry['amount'])
        ext_transaction.internal_operation.amount_portfolio = 0.0
        ext_transaction.internal_operation.amount_management = 0.0
        ext_transaction.internal_operation.operation_date = entry['operation_date']
        ext_transaction.internal_operation.value_date = entry['value_date']
        ext_transaction.internal_operation.status = extract_status(entry['status'])
        ext_transaction.internal_operation.additional_information = {}
        ext_transaction.internal_operation.additional_description = {'aliases': {me.provider_code: entry['identifier']}}
        ext_transaction.internal_operation.operation_type = extract_operation_type(entry['movement_type'])
        ext_transaction.internal_operation.source = None
        ext_transaction.internal_operation.target = None
        ext_transaction.internal_operation.security = None
        ext_transaction.internal_operation.quantity = None
        ext_transaction.internal_operation.price = None
        LOGGER.debug('EAMCOM - Saving')
        ext_transaction.internal_operation.save()
        LOGGER.debug('EAMCOM - Reloading saved operation')
        ext_transaction.internal_operation = Operation.objects.get(id=ext_transaction.internal_operation.id)
        ext_transaction.save()
        results.append(ext_transaction)
    return done, results
        
        
def import_security_operations(data):
    done = True
    results = []
    for entry in data:
        try:
            portfolio = Portfolio.objects.get(identifier=entry['portfolio_id'])
        except:
            LOGGER.error('EAMCOM - Could not find portfolio with identifier [' + entry['portfolio_id'] + '] or too many results!')
            done = False
            break
        try:
            ext_transaction = ExternalTransaction.objects.get(provider=me, portfolio=portfolio, provider_identifier=entry['identifier'])
        except ExternalTransaction.DoesNotExist:
            ext_transaction = ExternalTransaction()
            ext_transaction.portfolio = portfolio
            ext_transaction.provider = me
            ext_transaction.provider_identifier = entry['identifier']
            ext_transaction.internal_operation = Operation()
            ext_transaction.is_imported = False
        f_account = None
        t_account = None
        e_security = None
        if entry['account_id'] not in [None, '', 'None']:
            try:
                LOGGER.debug('EAMCOM - Searching existing from account - [' + entry['account_id'] + ']')
                f_account = ExternalAccount.objects.get(provider=me, provider_identifier=entry['account_id'])
                LOGGER.debug('EAMCOM - Found')
            except ExternalAccount.DoesNotExist:
                LOGGER.debug('EAMCOM - Not found')
        if entry['security'] not in [None, '', 'None']:
            try:
                LOGGER.debug('EAMCOM - Searching existing security - [' + entry['security'] + ']')
                e_security = ExternalSecurity.objects.get(provider=me, provider_identifier=entry['security'], currency__identifier=entry['currency'])
                LOGGER.debug('EAMCOM - Found')
            except ExternalSecurity.DoesNotExist:
                LOGGER.debug('EAMCOM - Not found')
        ext_transaction.is_valid = (e_security!=None and e_security.associated!=None)
        ext_transaction.external_security = e_security
        ext_transaction.external_source = f_account
        ext_transaction.external_target = t_account
        LOGGER.debug('EAMCOM - Filling internal operation fields')
        ext_transaction.internal_operation.identifier = entry['identifier']
        ext_transaction.internal_operation.name = entry['label']
        ext_transaction.internal_operation.description = entry['label']
        ext_transaction.internal_operation.spot_rate = float(entry['spot_rate'])
        price_divisor = 1.0
        if e_security!=None and e_security.associated!=None:
            price_divisor = e_security.associated.get_price_divisor()
        ext_transaction.internal_operation.amount = float(entry['price']) * float(entry['quantity']) / price_divisor
        ext_transaction.internal_operation.amount_portfolio = 0.0
        ext_transaction.internal_operation.amount_management = 0.0
        ext_transaction.internal_operation.operation_date = entry['operation_date']
        ext_transaction.internal_operation.value_date = entry['value_date']
        ext_transaction.internal_operation.status = extract_status(entry['status'])
        ext_transaction.internal_operation.additional_information = {}
        ext_transaction.internal_operation.additional_description = {'aliases': {me.provider_code: entry['identifier']}}
        ext_transaction.internal_operation.operation_type = extract_operation_type(entry['movement_type'])
        ext_transaction.internal_operation.source = None
        ext_transaction.internal_operation.target = None
        ext_transaction.internal_operation.security = None
        ext_transaction.internal_operation.quantity = float(entry['quantity'])
        ext_transaction.internal_operation.price = float(entry['price'])
        LOGGER.debug('EAMCOM - Saving')
        ext_transaction.internal_operation.save()
        LOGGER.debug('EAMCOM - Reloading saved operation')
        ext_transaction.internal_operation = Operation.objects.get(id=ext_transaction.internal_operation.id)
        ext_transaction.save()
        results.append(ext_transaction)
    return done, results
        
        
        
        
        
        
        
        
        
        
        
        