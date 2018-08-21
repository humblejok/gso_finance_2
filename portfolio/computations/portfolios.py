'''
Created on 4 mars 2018

@author: sdejo
'''
import logging
import pandas as pd
from datetime import datetime as dt
from gso_finance_2.tracks_utility import get_track_content, set_track_content,\
    to_pandas
from portfolio.computations import security_accounts, cash_accounts
from portfolio.models import MoneyAccountChain

LOGGER = logging.getLogger(__name__)


def update_portfolio_model(portfolio):
    daily_performances = get_track_content('finance', portfolio.id, 'performance', expand_today=True)
    monthly_performances = get_track_content('finance', portfolio.id, 'mtd', expand_today=True)
    yearly_performances = get_track_content('finance', portfolio.id, 'ytd', expand_today=True)
    valuation = get_track_content('finance', portfolio.id, 'valuation', expand_today=True)
    valuation_mgmt = get_track_content('finance', portfolio.id, 'valuation_mgmt', expand_today=True)
    
    portfolio.last_computation = daily_performances[-1]['date']
    portfolio.previous_day = daily_performances[-2]['value']
    portfolio.week_to_date = 0.0 
    portfolio.month_to_date = monthly_performances[-1]['value']
    portfolio.quarter_to_date = 0.0
    portfolio.year_to_date = yearly_performances[-1]['value']
    portfolio.current_aum_local = valuation[-1]['value']
    portfolio.current_aum_mgmt = valuation_mgmt[-1]['value']
    portfolio.save()
    

def compute_accounts(portfolio):
    for account in portfolio.accounts.all():
        if account.type.identifier=='ACC_SECURITY':
            security_accounts.build_chain(account)
            security_accounts.compute_valuation(portfolio, account)
        else:
            MoneyAccountChain.build_chain(account)
            cash_accounts.build_chain(account)
            cash_accounts.compute_valuation(portfolio, account)

def compute_account_weight_and_update(portfolio, account):
    start_date = portfolio.inception_date.strftime('%Y-%m-%d')
    today = dt.today().strftime('%Y-%m-%d')
    dates_range = pd.date_range(start=start_date, end=today, freq='D')
    
    amount_local = get_track_content('finance', account.id, 'account', expand_today=True, nafill=0.0)
    amount_portfolio = get_track_content('finance', account.id, 'portfolio', expand_today=True, nafill=0.0)
    portfolio_valuation = get_track_content('finance', portfolio.id, 'valuation', expand_today=True, nafill=0.0)
    account.last_computation = amount_local[-1]['date']
    account.current_amount_local = amount_local[-1]['value']
    account.current_amount_portfolio = amount_portfolio[-1]['value']
    account.save()
    
    portfolio_data = to_pandas(portfolio_valuation)
    account_data = to_pandas(amount_portfolio)
    weight_data = pd.DataFrame()
    weight_data['value'] = (account_data['value'] / portfolio_data['value']).fillna(0.0)
    weight_data = weight_data.reindex(dates_range).fillna(0.0)
    weight_data['date'] = weight_data.index.strftime('%Y-%m-%d')
    set_track_content('finance', account.id, 'weight', weight_data.to_dict('records'), True)
            
def update_accounts(portfolio):
    for account in portfolio.accounts.all():
        if account.include_valuation:
            compute_account_weight_and_update(portfolio, account)
            if account.type.identifier=='ACC_SECURITY':
                security_accounts.update_valuation(portfolio, account)
            else:
                cash_accounts.update_valuation(portfolio, account)
    

def compute_valuation(portfolio):
    start_date = portfolio.inception_date.strftime('%Y-%m-%d')
    today = dt.today().strftime('%Y-%m-%d')
    dates_range = pd.date_range(start=start_date, end=today, freq='D')
    
    portfolio_valuation = None
    portfolio_valuation_mgmt = None
    portfolio_exist = False
    
    fop_movements = None
    fop_movements_exist = False
    
    no_pnl_mvts = None
    no_pnl_mvts_exist = False
    
    for account in portfolio.accounts.filter(include_valuation=True):
        if account.include_valuation:
            if account.type.identifier=='ACC_SECURITY':
                fop_mvts = get_track_content('finance', account.id, 'fop_portfolio', expand_today=True, nafill=0.0)
                fop_mvts = to_pandas(fop_mvts)
                fop_mvts = fop_mvts.reindex(dates_range).fillna(0.0)
                if not fop_movements_exist:
                    fop_movements = fop_mvts
                    fop_movements_exist = True
                else:
                    fop_movements['value'] = fop_movements['value'] + fop_mvts['value']
            else:
                mvt_no_pnl = get_track_content('finance', account.id, 'mvt_no_pnl_portfolio', expand_today=True)
                mvt_no_pnl = to_pandas(mvt_no_pnl)
                mvt_no_pnl = mvt_no_pnl.reindex(dates_range).fillna(0.0)
                if not  no_pnl_mvts_exist:
                    no_pnl_mvts = mvt_no_pnl
                    no_pnl_mvts_exist = True
                else:
                    no_pnl_mvts['value'] = no_pnl_mvts['value'] + mvt_no_pnl['value']
            portfolio_aum = get_track_content('finance', account.id, 'portfolio', expand_today=True)
            portfolio_mgmt = get_track_content('finance', account.id, 'mgmt', expand_today=True)
            portfolio_aum = to_pandas(portfolio_aum)
            portfolio_mgmt = to_pandas(portfolio_mgmt)
            portfolio_aum = portfolio_aum.reindex(dates_range).fillna(0.0)
            portfolio_mgmt = portfolio_mgmt.reindex(dates_range).fillna(0.0)
            if not portfolio_exist:
                portfolio_valuation = portfolio_aum
                portfolio_valuation_mgmt = portfolio_mgmt
                portfolio_exist = True
            else:
                portfolio_valuation['value'] = portfolio_valuation['value'] + portfolio_aum['value']
                portfolio_valuation_mgmt['value'] = portfolio_valuation_mgmt['value'] + portfolio_mgmt['value']
                
    if not portfolio_exist:
        portfolio_valuation = pd.DataFrame(index=dates_range, columns=['value']).fillna(0.0)
    
    if not fop_movements_exist:
        fop_movements = pd.DataFrame(index=dates_range, columns=['value']).fillna(0.0)
    
    if not no_pnl_mvts_exist:
        no_pnl_mvts = pd.DataFrame(index=dates_range, columns=['value']).fillna(0.0)
    valuation = pd.DataFrame()
    valuation['portfolio'] = portfolio_valuation['value']
    valuation['movements_no_pnl'] = no_pnl_mvts['value']
    valuation['movements_fop'] = fop_movements['value']
    shifted_valuation = valuation.shift(1, 'D').reindex(dates_range).fillna(0.0)
    valuation['portfolio_previous'] = shifted_valuation['portfolio']
    valuation['mdietz_up'] = valuation['portfolio'] - valuation['movements_fop'] - shifted_valuation['portfolio'] - valuation['movements_no_pnl']
    valuation['mdietz_down'] = shifted_valuation['portfolio'] + valuation['movements_fop'] + valuation['movements_no_pnl']
    valuation['performance'] = (valuation['mdietz_up'] /  valuation['mdietz_down']).fillna(0.0)
    performance = pd.DataFrame(valuation['performance']).rename(columns={'performance': 'value'})
    mtd = performance.groupby([(performance.index.year), (performance.index.month)]).apply(lambda x:x.add(1).cumprod())-1
    ytd = performance.groupby(performance.index.year).apply(lambda x:x.add(1).cumprod()) - 1
    cumulated = (performance + 1).cumprod() * 100
    cumulated = cumulated.fillna(100.0)
    performance['date'] = performance.index.strftime('%Y-%m-%d')
    set_track_content('finance', portfolio.id, 'performance', performance.to_dict('records'), True)
    cumulated['date'] = cumulated.index.strftime('%Y-%m-%d')
    set_track_content('finance', portfolio.id, 'cumulated', cumulated.to_dict('records'), True)
    ytd['date'] = ytd.index.strftime('%Y-%m-%d')
    set_track_content('finance', portfolio.id, 'ytd', ytd.to_dict('records'), True)
    mtd['date'] = mtd.index.strftime('%Y-%m-%d')
    set_track_content('finance', portfolio.id, 'mtd', mtd.to_dict('records'), True)
    portfolio_valuation['date'] = portfolio_valuation.index.strftime('%Y-%m-%d')
    set_track_content('finance', portfolio.id, 'valuation', portfolio_valuation.to_dict('records'), True)
    portfolio_valuation_mgmt['date'] = portfolio_valuation_mgmt.index.strftime('%Y-%m-%d')
    set_track_content('finance', portfolio.id, 'valuation_mgmt', portfolio_valuation_mgmt.to_dict('records'), True)