'''
Created on 18 août 2018

@author: sdejo
'''
from django.conf.urls import url
from eamcom.views import get_positions, get_cash_operations,\
    get_security_operations

urlpatterns = [
    url('positions/(?P<portfolio_id>.+)/$', get_positions),
    url('operations_cash/(?P<portfolio_id>.+)/$', get_cash_operations),
    url('operations_security/(?P<portfolio_id>.+)/$', get_security_operations),
    ]