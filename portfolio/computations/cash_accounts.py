'''
Created on 25 févr. 2018

@author: sdejo
'''
from django.db.models import Q
from gso_finance_2.tracks_utility import set_track_content, get_track_content
from gso_finance_2.utility import my_class_import
from security import forex_utility

import pandas as pd


def build_chain(account):
    Operation = my_class_import('portfolio.models.Operation')
    all_operations = Operation.objects.filter(Q(source__id=account.id) | Q(target__id=account.id)).distinct().order_by('value_date', 'id')
    
    history = []
    mvt_pnl = {}
    mvt_no_pnl = {}
    amount = 0.0
    for operation in all_operations:
        key_date = operation.value_date.strftime('%Y-%m-%d')
        if key_date not in mvt_pnl:
            mvt_pnl[key_date] = 0.0
        if key_date not in mvt_no_pnl:
            mvt_no_pnl[key_date] = 0.0
        print('Operation:' + operation.name + ' === ' + str(operation.amount))
        operation_amount = operation.amount
        if operation.status.identifier!='OPE_CANCELLED':
            if operation.target!=None and operation.security==None:
                if operation.target.id==account.id:
                    operation_amount = operation_amount * operation.spot_rate
                else:
                    operation_amount = operation_amount * -1.0
            if operation.security!=None:
                operation_amount = operation_amount * operation.spot_rate * (-1.0 if operation.operation_type.identifier in ['OPE_TYPE_BUY'] else 1.0)
            if operation.target==None and operation.source!=None:
                operation_amount = operation_amount * operation.spot_rate
        else:
            operation_amount = 0.0
        amount = amount + operation_amount
        history.append({'date': key_date, 'value': amount})
        if operation.operation_type.identifier in ['OPE_TYPE_FEES','OPE_TYPE_ACCRUED_PAYMENT','OPE_TYPE_COUPON', 'OPE_TYPE_DIVIDEND', 'OPE_TYPE_COMMISSION', 'OPE_TYPE_TAX', 'OPE_TYPE_PNL']:
            mvt_pnl[key_date] = mvt_pnl[key_date] + operation_amount
        elif operation.operation_type.identifier not in ['OPE_TYPE_BUY', 'OPE_TYPE_SELL', 'OPE_TYPE_BUY_FOP', 'OPE_TYPE_SELL_FOP']:
            mvt_no_pnl[key_date] = mvt_no_pnl[key_date] + operation_amount
            
    set_track_content('finance', account.id, 'cash', history, True)
    set_track_content('finance', account.id, 'mvt_pnl', [{'date': key, 'value': mvt_pnl[key]} for key in mvt_pnl], True)
    set_track_content('finance', account.id, 'mvt_no_pnl', [{'date': key, 'value': mvt_no_pnl[key]} for key in mvt_no_pnl], True)

def compute_valuation(portfolio, account):
    history = get_track_content('finance', account.id, 'cash', expand_today=True)
    history = pd.DataFrame(history)
    history = history.set_index('date')
    history.index = pd.to_datetime(history.index)
    history =  history.rename(columns={'value': 'account'})
    
    mvt_pnl = get_track_content('finance', account.id, 'mvt_pnl', expand_today=True, nafill=0.0)
    mvt_pnl = pd.DataFrame(mvt_pnl)
    mvt_pnl = mvt_pnl.set_index('date')
    mvt_pnl.index = pd.to_datetime(mvt_pnl.index)
    mvt_pnl =  mvt_pnl.rename(columns={'value': 'account'})
    
    mvt_no_pnl = get_track_content('finance', account.id, 'mvt_no_pnl', expand_today=True, nafill=0.0)
    mvt_no_pnl = pd.DataFrame(mvt_no_pnl)
    mvt_no_pnl = mvt_no_pnl.set_index('date')
    mvt_no_pnl.index = pd.to_datetime(mvt_no_pnl.index)
    mvt_no_pnl =  mvt_no_pnl.rename(columns={'value': 'account'})
    
    if account.currency.identifier!=portfolio.currency.identifier:
        spot_portfolio = pd.DataFrame(forex_utility.find_spot_track(account.currency.identifier, portfolio.currency.identifier))
        spot_portfolio = spot_portfolio.set_index('date')
        spot_portfolio.index = pd.to_datetime(spot_portfolio.index)
        spot_portfolio = spot_portfolio.reindex(history.index)
        history['portfolio'] = history['account'] * spot_portfolio['value']
        mvt_pnl['portfolio'] = mvt_pnl['account'] * spot_portfolio['value']
        mvt_no_pnl['portfolio'] = mvt_no_pnl['account'] * spot_portfolio['value']
    else:
        history['portfolio'] = history['account']
        mvt_pnl['portfolio'] = mvt_pnl['account']
        mvt_no_pnl['portfolio'] = mvt_no_pnl['account']
        
    if account.currency.identifier!=portfolio.management_company.base_currency.identifier:
        spot_mgmt = pd.DataFrame(forex_utility.find_spot_track(account.currency.identifier, portfolio.management_company.base_currency.identifier))
        spot_mgmt = spot_mgmt.set_index('date')
        spot_mgmt.index = pd.to_datetime(spot_mgmt.index)
        spot_mgmt = spot_mgmt.reindex(history.index)
        history['mgmt'] = history['account'] * spot_mgmt['value']
        mvt_pnl['mgmt'] = mvt_pnl['account'] * spot_mgmt['value']
        mvt_no_pnl['mgmt'] = mvt_no_pnl['account'] * spot_mgmt['value']
    else:
        history['mgmt'] = history['account']
        mvt_pnl['mgmt'] = mvt_pnl['account']
        mvt_no_pnl['mgmt'] = mvt_no_pnl['account']
        
    account_amount = pd.DataFrame(history['account']).rename(columns={'account': 'value'})
    account_amount['date'] = account_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'account', account_amount.to_dict('records'), True)
    portfolio_amount = pd.DataFrame(history['portfolio']).rename(columns={'portfolio': 'value'})
    portfolio_amount['date'] = portfolio_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'portfolio', portfolio_amount.to_dict('records'), True)
    mgmt_amount = pd.DataFrame(history['mgmt']).rename(columns={'mgmt': 'value'})
    mgmt_amount['date'] = mgmt_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'mgmt', mgmt_amount.to_dict('records'), True)
    
    portfolio_amount = pd.DataFrame(mvt_pnl['portfolio']).rename(columns={'portfolio': 'value'})
    portfolio_amount['date'] = portfolio_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'mvt_pnl_portfolio', portfolio_amount.to_dict('records'), True)
    mgmt_amount = pd.DataFrame(mvt_pnl['mgmt']).rename(columns={'mgmt': 'value'})
    mgmt_amount['date'] = mgmt_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'mvt_pnl_mgmt', mgmt_amount.to_dict('records'), True)
    
    portfolio_amount = pd.DataFrame(mvt_no_pnl['portfolio']).rename(columns={'portfolio': 'value'})
    portfolio_amount['date'] = portfolio_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'mvt_no_pnl_portfolio', portfolio_amount.to_dict('records'), True)
    mgmt_amount = pd.DataFrame(mvt_no_pnl['mgmt']).rename(columns={'mgmt': 'value'})
    mgmt_amount['date'] = mgmt_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'mvt_nop_pnl_mgmt', mgmt_amount.to_dict('records'), True)
    