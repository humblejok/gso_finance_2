'''
Created on 25 févr. 2018

@author: sdejo
'''
from django.db.models import Q
from gso_finance_2.tracks_utility import set_multi_content, set_track_content,\
    get_multi_content, get_track_content, to_pandas, from_pandas
from gso_finance_2.utility import my_class_import

import pandas as pd
import copy
from security.models import Security
from security import forex_utility
from datetime import datetime as dt

def build_chain(account):
    Operation = my_class_import('portfolio.models.Operation')
    all_operations = Operation.objects.filter(Q(target__id=account.id), Q(operation_type__identifier__in=['OPE_TYPE_BUY', 'OPE_TYPE_BUY_FOP', 'OPE_TYPE_SELL', 'OPE_TYPE_SELL_FOP'])).distinct().order_by('value_date', 'id')
    
    previous_date = None
    
    positions = {}
    buy_prices = {}
    decrease = []
    increase = []
    increase_fop = []
    decrease_fop = []
    
    for operation in all_operations:
        if operation.status.identifier!='OPE_STATUS_CANCELLED':
            key_date = operation.value_date.strftime('%Y-%m-%d')
            key_security = str(operation.security.id)
            print('Operation:' + operation.name + ' as of ' + operation.value_date.strftime('%Y-%m-%d'))
            if key_date not in positions:
                positions[key_date] = {} if previous_date not in positions else copy.deepcopy(positions[previous_date])
                buy_prices[key_date] = {} if previous_date not in buy_prices else copy.deepcopy(buy_prices[previous_date])
                decrease.append({'date': key_date, 'value': 0.0})
                increase.append({'date': key_date, 'value': 0.0})
                increase_fop.append({'date': key_date, 'value': 0.0})
                decrease_fop.append({'date': key_date, 'value': 0.0})
            if not key_security in positions[key_date]:
                print('New position')
                positions[key_date][key_security] = operation.quantity
                buy_prices[key_date][key_security] = operation.price
            else:
                print('Existing position')
                positions[key_date][key_security] = positions[key_date][key_security] + (operation.quantity * (1.0 if 'BUY' in operation.operation_type.identifier else -1.0))
                buy_prices[key_date][key_security] = (((operation.price * operation.quantity) + (positions[key_date][key_security] * buy_prices[key_date][key_security])) / positions[key_date][key_security]) if 'BUY' in operation.operation_type.identifier and positions[key_date][key_security]!=0.0 else buy_prices[key_date][key_security]
            if 'BUY' in operation.operation_type.identifier:
                if 'FOP' in operation.operation_type.identifier:
                    increase_fop[-1]['value'] = increase_fop[-1]['value'] + (operation.price * operation.quantity) / operation.security.get_price_divisor()
                else:
                    increase[-1]['value'] = increase[-1]['value'] + (operation.price * operation.quantity) / operation.security.get_price_divisor()
            else:
                if 'FOP' in operation.operation_type.identifier:
                    decrease_fop[-1]['value'] = decrease_fop[-1]['value'] + (operation.price * operation.quantity) / operation.security.get_price_divisor()
                else:
                    decrease[-1]['value'] = decrease[-1]['value'] + (operation.price * operation.quantity) / operation.security.get_price_divisor()
            previous_date = key_date
    set_multi_content('finance', account.id, 'positions', positions, True)
    set_multi_content('finance', account.id, 'buy_prices', buy_prices, True)
    set_track_content('finance', account.id, 'decrease', decrease, True)
    set_track_content('finance', account.id, 'increase', increase, True)
    set_track_content('finance', account.id, 'increase_fop', increase_fop, True)
    set_track_content('finance', account.id, 'decrease_fop', decrease_fop, True)
    
def compute_valuation(portfolio, account):
    positions = get_multi_content('finance', account.id, 'positions')
    if len(positions)==0:
        return
    positions = [{**{'date': token['date']}, **token['value']} for token in positions]
    positions = pd.DataFrame(positions)
    positions = positions.set_index('date')
    positions.index = pd.to_datetime(positions.index)
    
    increase_fop_mvts = get_track_content('finance', account.id, 'increase_fop', expand_today=True, nafill=0.0)
    decrease_fop_mvts = get_track_content('finance', account.id, 'decrease_fop', expand_today=True, nafill=0.0)
    
    increase_fop_mvts = pd.DataFrame(increase_fop_mvts)
    increase_fop_mvts = increase_fop_mvts.set_index('date')
    increase_fop_mvts.index = pd.to_datetime(increase_fop_mvts.index)
    decrease_fop_mvts = pd.DataFrame(decrease_fop_mvts)
    decrease_fop_mvts = decrease_fop_mvts.set_index('date')
    decrease_fop_mvts.index = pd.to_datetime(decrease_fop_mvts.index)
    fop_mvts = pd.DataFrame()
    fop_mvts['account'] = increase_fop_mvts['value'] - decrease_fop_mvts['value']
    tracks = []
    
    for security_id in positions:
        security = Security.objects.get(id=security_id)
        prices = get_track_content(security.provider.provider_code, security.provider_identifier, 'price', expand_today=True)
        prices = to_pandas(prices)
        prices = prices.rename(columns={'value': security_id})
        prices = prices / security.get_price_divisor()
        tracks.append(prices)
    prices = pd.concat(tracks, axis='columns').reindex(positions.index).bfill().ffill()
    holdings = positions * prices
    holdings = holdings.fillna(0.0)
    holdings['date'] = holdings.index.strftime('%Y-%m-%d')
    valued_holdings = from_pandas(holdings, True)
    set_multi_content('finance', account.id, 'valued_holdings', valued_holdings, True)
    holdings = holdings.drop('date', axis=1)
    holdings['account'] = holdings.sum(axis='columns')
    if security.currency.identifier!=portfolio.currency.identifier:
        spot_portfolio = pd.DataFrame(forex_utility.find_spot_track(security.currency.identifier, portfolio.currency.identifier))
        spot_portfolio = to_pandas(spot_portfolio)
        spot_portfolio = spot_portfolio.reindex(holdings.index)
        holdings['portfolio'] = holdings['account'] * spot_portfolio['value']
        fop_mvts['portfolio'] = fop_mvts['account'] * spot_portfolio['value']
    else:
        holdings['portfolio'] = holdings['account']
        fop_mvts['portfolio'] = fop_mvts['account']
    if security.currency.identifier!=portfolio.management_company.base_currency.identifier:
        spot_mgmt = pd.DataFrame(forex_utility.find_spot_track(security.currency.identifier, portfolio.management_company.base_currency.identifier))
        spot_mgmt = to_pandas(spot_mgmt)
        spot_mgmt = spot_mgmt.reindex(holdings.index)
        holdings['mgmt'] = holdings['account'] * spot_mgmt['value']
        fop_mvts['mgmt'] = fop_mvts['account'] * spot_mgmt['value']
    else:
        holdings['mgmt'] = holdings['account']
        fop_mvts['mgmt'] = fop_mvts['account']
        
    account_amount = pd.DataFrame(holdings['account']).rename(columns={'account': 'value'})
    account_amount['date'] = account_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'account', account_amount.to_dict('records'), True)
    portfolio_amount = pd.DataFrame(holdings['portfolio']).rename(columns={'portfolio': 'value'})
    portfolio_amount['date'] = portfolio_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'portfolio', portfolio_amount.to_dict('records'), True)
    mgmt_amount = pd.DataFrame(holdings['mgmt']).rename(columns={'mgmt': 'value'})
    mgmt_amount['date'] = mgmt_amount.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'mgmt', mgmt_amount.to_dict('records'), True)
    
    account_fop = pd.DataFrame(fop_mvts['account']).rename(columns={'account': 'value'})
    account_fop['date'] = account_fop.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'fop_account', account_fop.to_dict('records'), True)
    portfolio_fop = pd.DataFrame(fop_mvts['portfolio']).rename(columns={'portfolio': 'value'})
    portfolio_fop['date'] = portfolio_fop.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'fop_portfolio', portfolio_fop.to_dict('records'), True)
    mgmt_fop = pd.DataFrame(fop_mvts['mgmt']).rename(columns={'mgmt': 'value'})
    mgmt_fop['date'] = mgmt_fop.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'fop_mgmt', mgmt_fop.to_dict('records'), True)
    
def update_valuation(portfolio, account):
    start_date = portfolio.inception_date.strftime('%Y-%m-%d')
    today = dt.today().strftime('%Y-%m-%d')
    dates_range = pd.date_range(start=start_date, end=today, freq='D')
    
    all_positions = get_multi_content('finance', account.id, 'valued_holdings', expand_today=True)
    all_positions = to_pandas(all_positions, multi=True)
    all_positions = all_positions.reindex(dates_range).fillna(0.0)
    
    amount_local = get_track_content('finance', account.id, 'account', expand_today=True)
    amount_local = to_pandas(amount_local)
    amount_local = amount_local.reindex(dates_range).fillna(0.0)
    
    account_weights = get_track_content('finance', account.id, 'weight', expand_today=True)
    account_weights = to_pandas(account_weights)
    account_weights = account_weights.reindex(dates_range).fillna(0.0)      
                    
    all_positions_local = all_positions.div(amount_local['value'], axis=0).fillna(0.0)
    all_positions_portfolio = all_positions_local.mul(account_weights['value'], axis=0).fillna(0.0)

    all_positions_local['date'] = all_positions_local.index.strftime('%Y-%m-%d')
    all_positions_local = from_pandas(all_positions_local, True)
    set_multi_content('finance', account.id, 'holdings_weights_local', all_positions_local, True)

    all_positions_portfolio['date'] = all_positions_portfolio.index.strftime('%Y-%m-%d')
    all_positions_portfolio = from_pandas(all_positions_portfolio, True)
    set_multi_content('finance', account.id, 'holdings_weights_portfolio', all_positions_portfolio, True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    