from django.shortcuts import render
from django.apps import apps 
from eamcom.apps import EamcomConfig
import logging

app_config = apps.get_app_config(EamcomConfig.name)

LOGGER = logging.getLogger(__name__)

def retrieve_positions(request, provider_identifier, portfolio_identifier):
    app_config.base_url