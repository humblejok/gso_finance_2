from django.shortcuts import render
from django.apps import apps 
from eamcom.apps import EamcomConfig

app_config = apps.get_app_config(EamcomConfig.name)