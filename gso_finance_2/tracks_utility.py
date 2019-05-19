'''
Created on 30 janv. 2018

@author: sdejo
'''

from json import dumps

import logging
import base64
import requests
import pandas as pd

SOURCES = {'novastone': {'url': 'http://jiren:5003/query', 'escape': False},
           #'finance': {'url': 'https://f2positions.providers.finance2.ch/query', 'escape': False},
           'finance': {'url': 'https://f2-novastone.providers.finance2.ch/query', 'escape': False},
           'vpbank': {'url': 'http://jiren:5001/query', 'escape': False},
           'bloomberg': {'url': 'https://bloomberg.providers.finance2.ch/query', 'escape': True},
           'pictet_provider': {'url': 'https://pictet-securities.finance2.ch/query', 'escape': False}}

STATISTICS_ENGINE = 'http://localhost:1664/compute'
LOGGER = logging.getLogger(__name__)
HEADERS = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}

class FStoryClient(object):

    response = None
    
    source_key = 'finance'
        
    def __init__(self, source_key='finance'):
        self.source_key = source_key
        
    def request(self, query):
        _response = requests.post(SOURCES[self.source_key.lower()]['url'], data=dumps(query), headers=HEADERS)
        if _response.status_code==200:
            self.response = _response.json()
            if 'data' in self.response:
                self.response = self.response['data']
        else:
            self.response = []
        return self.response

def from_pandas(data, multi=False):
    if multi:
        return { record['date'] : {token: record[token] for token in record if token!='date'} for record in data.to_dict('records') }
    else:
        data['date'] = data.index.strftime('%Y-%m-%d')
        return data.to_dict('records')

def to_pandas(data, multi=False):
    df = pd.DataFrame(data)
    df = df.set_index('date')
    df.index = pd.to_datetime(df.index)
    if multi:
        df = df['value'].apply(pd.Series).fillna(0.0)
    return df

def get_track_content(source_key, entity_id, track_type, ascending = True, divisor = 1.0, substract = 0.0, expand_today=False, nofill=False, nafill=None):
    if SOURCES[source_key.lower()]['escape']:
        try:
            container_id = 'entity_' + base64.b64encode(entity_id, '+-'.encode('utf8')).decode('utf8')
        except:
            container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
    else:
        container_id = 'entity_' + str(entity_id)
    f_client = FStoryClient(source_key)
    if divisor==1.0 and substract==0.0 and ascending:
        track_id = 'track_' + str(track_type)
        query = {'command': 'ordered', 'collection_name': container_id, 'element_id': track_id, 'nofill': nofill, 'expand_today': expand_today}
        if nafill!=None:
            query['nafill'] = nafill
        raw_values = f_client.request(query)
        LOGGER.info('Loaded track content of ' + container_id + ' - ' + track_id + ' with ' + str(len(raw_values)) + ' elements.')
        return raw_values
    else:
        track_id = 'track_' + str(track_type)
        raw_values = f_client.request({'command': 'ordered', 'collection_name': container_id, 'element_id': track_id, 'nofill': True})
        LOGGER.info('Track content loaded from ' + container_id + '.' + track_id + ' with ' + str(len(raw_values)) + ' elements.')
        data = [{'date':value['date'], 'value': (value[u'value']/divisor) - substract } for value in raw_values]
        # TODO: Implement ascending(true/false)
        return data

def clean_track_content(source_key, entity_id, track_type):
    if SOURCES[source_key.lower()]['escape']:
        container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
    else:
        container_id = 'entity_' + str(entity_id)
    track_id = 'track_' + str(track_type)
    f_client = FStoryClient(source_key)
    f_client.request({'command': 'set', 'collection_name': container_id, 'element_id': track_id, 'data': {}})

def set_track_content(source_key, entity_id, track_type, values, clean):
    LOGGER.info('Storing track content')
    if SOURCES[source_key.lower()]['escape']:
        try:
            container_id = 'entity_' + base64.b64encode(entity_id, '+-'.encode('utf8')).decode('utf8')
        except:
            container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
    else:
        container_id = 'entity_' + str(entity_id.decode('utf8'))
    track_id = 'track_' + str(track_type)
    # TODO: Historical formatting, keep it?
    clean_values = {value['date'] if isinstance(value['date'], str) else value['date'].strftime('%Y-%m-%d'): value['value'] for value in values}
    f_client = FStoryClient(source_key)
    f_client.request({'command': 'set' if clean else 'update', 'collection_name': container_id, 'element_id': track_id, 'data': clean_values})
    LOGGER.info('Track content stored as ' + container_id + '.' + track_id + ' with ' + str(len(values)) + (' updated' if not clean else '') + ' elements.')

def compute_track_content(source_key, entity_id, track_type, engine_name, target_type):
    if SOURCES[source_key.lower()]['escape']:
        try:
            container_id = 'entity_' + base64.b64encode(entity_id, '+-'.encode('utf8')).decode('utf8')
        except:
            container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
    else:
        container_id = 'entity_' + str(entity_id)
    track_id = 'track_' + str(track_type)
    f_client = FStoryClient(source_key)
    f_client.request({'command': 'compute', 'collection_name': container_id, 'element_id': track_id, 'arguments':[engine_name, container_id, 'track_' + str(target_type)]})
    return get_track_content(source_key, entity_id, target_type)

def get_multi_last(source_key, entity_id, data_type):
    if SOURCES[source_key.lower()]['escape']:
        try:
            container_id = 'entity_' + base64.b64encode(entity_id, '+-'.encode('utf8')).decode('utf8')
        except:
            container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
    else:
        container_id = 'entity_' + str(entity_id)
    f_client = FStoryClient(source_key)
    query = {'command': 'filter', 'filter_type': 'last', 'collection_name': container_id, 'element_id': data_type, 'expand_today': True, 'nofill': False}
    raw_values = f_client.request(query)
    LOGGER.info('Loaded track content of ' + container_id + ' - ' + data_type + ' with ' + str(len(raw_values)) + ' elements.')
    return raw_values
    
def get_multi_content(source_key, entity_id, data_type, expand_today=True, nofill=False, nafill=None):
    if SOURCES[source_key.lower()]['escape']:
        try:
            container_id = 'entity_' + base64.b64encode(entity_id, '+-'.encode('utf8')).decode('utf8')
        except:
            container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
    else:
        container_id = 'entity_' + str(entity_id)
    f_client = FStoryClient(source_key)
    query = {'command': 'ordered', 'collection_name': container_id, 'element_id': data_type, 'expand_today': expand_today, 'nofill': nofill}
    if nafill!=None:
        query['nafill'] = nafill
    raw_values = f_client.request(query)
    LOGGER.info('Loaded track content of ' + container_id + ' - ' + data_type + ' with ' + str(len(raw_values)) + ' elements.')
    return raw_values
    
def set_multi_content(source_key, entity_id, data_type, values, clean):
    LOGGER.info('Storing track content')
    if SOURCES[source_key.lower()]['escape']:
        try:
            container_id = 'entity_' + base64.b64encode(entity_id, '+-'.encode('utf8')).decode('utf8')
        except:
            container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
    else:
        container_id = 'entity_' + str(entity_id)
    f_client = FStoryClient(source_key)
    f_client.request({'command': 'set' if clean else 'update', 'collection_name': container_id, 'element_id': data_type, 'data': values})
    LOGGER.info('Track content stored as ' + container_id + '.' + data_type + ' with ' + str(len(values)) + (' updated' if not clean else '') + ' elements.')
    new_values = get_multi_content(source_key, entity_id, data_type)
    return new_values
