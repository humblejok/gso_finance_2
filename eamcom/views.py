from django.apps import apps 
from eamcom.apps import EamcomConfig
import logging
from django.views.decorators.http import require_http_methods
from django.http.response import HttpResponseGone, HttpResponseNotFound,\
    HttpResponseNotAllowed, JsonResponse, HttpResponseBadRequest,\
    HttpResponseServerError
import requests
from portfolio.models import Portfolio
from json import dumps
from eamcom.utility import import_positions, create_security_holdings,\
    create_account_holdings
from providers.models import ExternalPortfolioHoldings
from datetime import datetime as dt
from common.models import Company

app_config = apps.get_app_config(EamcomConfig.name)

LOGGER = logging.getLogger(__name__)

me = Company.objects.get(provider_code='EAMCOM')

@require_http_methods(["GET"])
def get_positions(request, portfolio_id):
    LOGGER.debug('EAMCOM - Getting positions for [' + portfolio_id + ']')
    if app_config.base_url==None:
        LOGGER.debug('EAMCOM - Misconfiguration or unavailble service')
        return HttpResponseGone()
    else:
        try:
            LOGGER.debug('EAMCOM - Loading portfolio and data')
            portfolio = Portfolio.objects.get(id=portfolio_id)
            if portfolio.bank==None or portfolio.bank.provider_code in ['', 'None', None]:
                return HttpResponseNotAllowed()
            provider_identifier = portfolio.bank.provider_code
            proxy_response = requests.get(app_config.base_url + '/executeRequest/positions/' + provider_identifier + '/' + portfolio.identifier + '/')
            if proxy_response.status_code>=200 and proxy_response.status_code<300:
                content = proxy_response.json()
                if content['request_success']:
                    status = import_positions(content['response_body'])
                    if not status:
                        return HttpResponseServerError('EAMCOM - An error occurred while importing external data')
                    LOGGER.debug('EAMCOM - Removing existing holdings as of today')
                    try:
                        holdings = ExternalPortfolioHoldings.objects.get(provider=me, portfolio=portfolio, application_date=dt.today())
                        holdings.security_holdings.all().delete()
                        holdings.account_holdings.all().delete()
                        holdings.delete()
                        LOGGER.debug('EAMCOM - Holdings removed')
                    except:
                        LOGGER.debug('EAMCOM - No previous holdings')
                    holdings = ExternalPortfolioHoldings()
                    holdings.provider = me
                    holdings.portfolio = portfolio
                    holdings.application_date = dt.today()
                    holdings.save()
                    securities_status, holdings.security_holdings = create_security_holdings(holdings, content['response_body'])
                    accounts_status, holdings.account_holdings = create_account_holdings(holdings, content['response_body'])
                    if not accounts_status or not securities_status:
                        LOGGER.error('EAMCOM - An error occurred during holdings import')
                    return JsonResponse(content['response_body'], safe=False)
                else:
                    LOGGER.error('EAMCOM - An error occurred while calling EAMCOM, see details below.')
                    LOGGER.error(dumps(content))
                    return HttpResponseBadRequest('EAMCOM - An error occurred while calling EAMCOM, please check the log file!')
        except Portfolio.DoesNotExist:
            return HttpResponseNotFound()