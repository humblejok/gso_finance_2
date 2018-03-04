'''
Created on 4 mars 2018

@author: sdejo
'''
import logging
import pandas as pd
from datetime import datetime as dt
from gso_finance_2.tracks_utility import get_track_content
from portfolio.computations import security_accounts, cash_accounts


LOGGER = logging.getLogger(__name__)

def compute_accounts(portfolio):
    for account in portfolio.accounts.all():
        if account.type.identifier=='ACC_SECURITY':
            security_accounts.build_chain(account)
            security_accounts.compute_valuation(portfolio, account)
        else:
            cash_accounts.build_chain(account)
            cash_accounts.compute_valuation(portfolio, account)
    

def compute_valuation(portfolio):
    start_date = portfolio.inception_date.strftime('%Y-%m-%d')
    today = dt.today().strftime('%Y-%m-%d')
    dates_range = pd.date_range(start=start_date, end=today, freq='D')
    
    portfolio_valuation = None
    portfolio_exist = False
    
    fop_movements = None
    fop_movements_exist = False
    
    no_pnl_mvts = None
    no_pnl_mvts_exist = False
    
    for account in portfolio.accounts.filter(include_valuation=True):
        if account.type.identifier=='ACC_SECURITY':
            fop_mvts = get_track_content('finance', account.id, 'fop_portfolio', expand_today=True)
            fop_mvts = pd.DataFrame(fop_mvts)
            fop_mvts = fop_mvts.set_index('date')
            fop_mvts.index = pd.to_datetime(fop_mvts.index)
            if not fop_movements_exist:
                fop_movements = fop_mvts
                fop_movements_exist = True
            else:
                fop_movements['value'] = fop_movements['value'] + fop_mvts['value']
        else:
            mvt_no_pnl = get_track_content('finance', account.id, 'mvt_no_pnl_portfolio', expand_today=True)
            mvt_no_pnl = pd.DataFrame(mvt_no_pnl)
            mvt_no_pnl = mvt_no_pnl.set_index('date')
            mvt_no_pnl.index = pd.to_datetime(mvt_no_pnl.index)
            if not  no_pnl_mvts_exist:
                no_pnl_mvts = mvt_no_pnl
                no_pnl_mvts_exist = True
            else:
                no_pnl_mvts['value'] = no_pnl_mvts['value'] + mvt_no_pnl['value']
            
            
        portfolio = get_track_content('finance', account.id, 'portfolio', expand_today=True)
        portfolio = pd.DataFrame(portfolio)
        portfolio = portfolio.set_index('date')
        portfolio.index = pd.to_datetime(portfolio.index)
        if not portfolio_exist:
            portfolio_valuation = portfolio
            portfolio_exist = True
        else:
            portfolio_valuation['value'] = portfolio_valuation['value'] + portfolio['value']
                
    if not portfolio_exist:
        portfolio_valuation = pd.DataFrame(index=dates_range, columns=['value']).fillna(0.0)
    portfolio_valuation = portfolio_valuation.reindex(dates_range).fillna(0.0)
    
    if not fop_movements_exist:
        fop_movements = pd.DataFrame(index=dates_range, columns=['value']).fillna(0.0)
    fop_movements = fop_movements.reindex(dates_range).fillna(0.0)
    
    if not no_pnl_mvts_exist:
        no_pnl_mvts = pd.DataFrame(index=dates_range, columns=['value']).fillna(0.0)
    no_pnl_mvts = no_pnl_mvts.reindex(dates_range).fillna(0.0)
    
    valuation = pd.DataFrame()
    valuation['portfolio'] = portfolio_valuation['value']
    valuation['movements_no_pnl'] = no_pnl_mvts['value']
    valuation['movements_fop'] = fop_movements['value']
    print(valuation)
    shifted_valuation = valuation.shift(1, 'D').reindex(dates_range).fillna(0.0)
    print(shifted_valuation)
    valuation['mdietz_up'] = valuation['portfolio'] - valuation['movements_fop'] - shifted_valuation['portfolio'] - valuation['movements_no_pnl']
    valuation['mdietz_down'] = shifted_valuation['portfolio'] + valuation['movements_fop'] + valuation['movements_no_pnl']
    valuation['performance'] = valuation['mdietz_up'] /  valuation['mdietz_down'] 
    print(valuation)
    return valuation