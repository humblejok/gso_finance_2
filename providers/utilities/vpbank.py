'''
Created on 2 janv. 2018

@author: sdejo
'''
from providers.models import VP_Position, VP_PositionType, VP_PositionTypeMap,\
    ExternalSecurity, ExternalSecurityPrice

from datetime import datetime as dt
from security.models import SecurityType
from common.models import Currency, Company

import logging

LOGGER = logging.getLogger(__name__)

def extract_securities():
    LOGGER.info('*** Extracting securities for VP BANK ***')
    vp_bank = Company.objects.get(default_name='VP Bank')
    security_vp_ids = VP_PositionType.objects.filter(default_name='security.models.Security').values_list('identifier', flat=True)
    all_positions = VP_Position.objects.filter(treated=False, data__InstrCode__in=security_vp_ids)
    for position in all_positions:
        LOGGER.info('Working on position ' + position.data['SecTxt'] + '/' + position.data['SecNo'])
        external_security = ExternalSecurity.objects.filter(provider_identifier=position.data['SecNo'])
        if not external_security.exists():
            LOGGER.info('\tPosition does not exist, creating')
            type_map = VP_PositionTypeMap.objects.filter(identifier=position.data['InstrCode'])
            if type_map.exists():
                external_security = ExternalSecurity()
                external_security.name = position.data['SecTxt']
                external_security.type = SecurityType.objects.get(identifier=type_map[0].default_name)
                external_security.currency = Currency.objects.get(identifier=position.data['PosCur'])
                external_security.provider = vp_bank
                external_security.provider_identifier = position.data['SecNo']
                external_security.provider_data = position.data
                external_security.save()
                LOGGER.info('\tAssigning initial price')
                pricing = ExternalSecurityPrice()
                pricing.security = external_security
                pricing.pricing_history = {dt.strptime(position.data['SecPriceDate'], '%Y%m%d').strftime('%Y-%m-%d'): float(position.data['SecPrice'])}
                pricing.save()
            else:
                LOGGER.info('\tPosition type not found, logging and skipping')
                position.treated_date = dt.today()
                position.comment['error_default_message'] = 'Unknown instrument code [' + position.data['InstrCode'] + '], please update the VP_PositionTypeMap table'
                position.comment['error_code'] = 'VP_UNKNOWN_INSTRUMENT_CODE'
                position.save()
                continue
        else:
            LOGGER.info('\tPosition found, loading')
            external_security = external_security[0]
            LOGGER.info('\tAdditional pricing')
            pricing = ExternalSecurityPrice.objects.get(security__id=external_security.id)
            pricing.pricing_history[dt.strptime(position.data['SecPriceDate'], '%Y%m%d').strftime('%Y-%m-%d')] = float(position.data['SecPrice'])
            pricing.save()
            if external_security.source_id==None:
                LOGGER.info('\tLink to FinanCE security not found, logging and skipping')
                position.treated_date = dt.today()
                position.comment['error_default_message'] = 'Not associated yet, waiting for association'
                position.comment['error_code'] = 'PROVIDER_WAITING_FOR_ASSOCIATION'
                position.save()
                continue
            LOGGER.info('\tPreparing for account consolidation')
            position.treated_date = dt.today()
            position.comment['error_default_message'] = 'Position found, waiting for consolidation'
            position.comment['error_code'] = 'PROVIDER_WAITING_FOR_CONSOLIDATION'
            position.save()
    LOGGER.info('*** End of extraction securities for VP BANK ***')