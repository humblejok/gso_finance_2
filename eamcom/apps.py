from django.apps import AppConfig
import requests
from eamcom import app_settings
import logging

LOGGER = logging.getLogger(__name__)

class EamcomConfig(AppConfig):
    name = 'eamcom'
    base_url = None
  
    def ready(self):
        LOGGER.info('Retrieving [' + app_settings.EAM_PROXY_NAME + '] from [' + app_settings.EUREKA_URL + ']')
        eureka_response = requests.get(
            app_settings.EUREKA_URL + '/eureka/v2/apps/' + app_settings.EAM_PROXY_NAME,
            headers={'content-type':'application/json', 'accept': 'application/json'},
            json={},
            auth=app_settings.EUREKA_AUTH
        )
        if eureka_response.status_code>=200 and eureka_response.status_code<300:
            eureka_data = eureka_response.json()
            if 'application' in eureka_data and len(eureka_data['application']['instance'])>0:
                # TODO: Implement load balancing
                instance = eureka_data['application']['instance'][0]
                self.base_url = instance['homePageUrl']
                LOGGER.info('Proxy found at [' + self.base_url + ']')
        elif eureka_response.status_code==404:
            # TODO; Implement retry every ...
            LOGGER.error('Proxy is not registered, retry later!')
        else:
            LOGGER.error('Eureka is not responding, retry later!')
