'''
Created on 18 août 2018

@author: sdejo
'''
from django.conf.urls import url
from eamcom.views import get_positions

urlpatterns = [
    url('positions/(?P<portfolio_id>.+)/$', get_positions),
    ]