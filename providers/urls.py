'''
Created on 19 août 2018

@author: sdejo
'''

from django.conf.urls import url
from providers.views import create_account_from, assign_account_to,\
    accept_external_transaction

urlpatterns = [
    url('account/(?P<account_holding_id>.+)/portfolio/(?P<holdings_id>.+)/$', create_account_from),
    url('account/(?P<account_holding_id>.+)/assign/(?P<account_id>.+)/$', assign_account_to),
    url('transaction/accept/(?P<external_transaction_id>.+)/$', accept_external_transaction),
    ]