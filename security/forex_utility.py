'''
Created on 25 févr. 2018

@author: sdejo
'''
from security.models import Security
from gso_finance_2.tracks_utility import get_track_content

def find_spot_track(source_currency, target_currency, expand_today=True):
    # TODO: Adapt to something else than BB
    security = Security.objects.filter(provider_identifier=source_currency + target_currency + ' Curncy').order_by('provider')
    if security.exists():
        security = security[0]
        # TODO: Handle error and dual sources
    return get_track_content(security.provider.provider_code, security.provider_identifier, 'price', expand_today=expand_today)
    