'''
Created on 30 janv. 2018

@author: sdejo
'''

from json import dumps

import logging
import base64
import requests

SOURCES = {'novastone': {'url': 'http://jiren:5003/query', 'escape': False},
           'finance': {'url': 'http://jiren:5002/query', 'escape': False},
           'vpbank': {'url': 'http://jiren:5001/query', 'escape': False},
           'bloomberg': {'url': 'http://jiren:5000/query', 'escape': True}}

LOGGER = logging.getLogger(__name__)
HEADERS = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}

class FStoryClient(object):

    response = None
    
    source_key = 'finance'
        
    def __init__(self, source_key='finance'):
        self.source_key = source_key
        
    def request(self, query):
        _response = requests.post(SOURCES[self.source_key]['url'], data=dumps(query), headers=HEADERS)
        if _response.status_code==200:
            self.response = _response.json()
            if 'data' in self.response:
                self.response = self.response['data']
        else:
            self.response = []
        return self.response

def get_track_content(source_key, entity_id, track_type, ascending = True, divisor = 1.0, substract = 0.0):
    if SOURCES[source_key]['escape']:
        try:
            container_id = 'entity_' + base64.b64encode(entity_id, '+-'.encode('utf8')).decode('utf8')
            print("BINARY")
        except:
            container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
        print("OUT->" + container_id)
    else:
        container_id = 'entity_' + str(entity_id)
    if divisor==1.0 and substract==0.0 and ascending:
        f_client = FStoryClient(source_key)
        track_id = 'track_' + str(track_type)
        raw_values = f_client.request({'command': 'ordered', 'collection_name': container_id, 'element_id': track_id})
        LOGGER.info('Loaded track content of ' + container_id + ' - ' + track_id + ' with ' + str(len(raw_values)) + ' elements.')
        return raw_values
    else:
        track_id = 'track_' + str(track_type)
        raw_values = f_client.request({'command': 'ordered', 'collection_name': container_id, 'element_id': track_id})
        LOGGER.info('Track content loaded from ' + container_id + '.' + track_id + ' with ' + str(len(raw_values)) + ' elements.')
        data = [{'date':value['date'], 'value': (value[u'value']/divisor) - substract } for value in raw_values]
        # TODO: Implement ascending(true/false)
        return data

def clean_track_content(source_key, entity_id, track_type):
    if SOURCES[source_key]['escape']:
        container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
    else:
        container_id = 'entity_' + str(entity_id)
    track_id = 'track_' + str(track_type)
    f_client = FStoryClient(source_key)
    f_client.request({'command': 'set', 'collection_name': container_id, 'element_id': track_id, 'data': {}})

def set_track_content(source_key, entity_id, track_type, values, clean):
    LOGGER.info('Storing track content')
    if SOURCES[source_key]['escape']:
        try:
            container_id = 'entity_' + base64.b64encode(entity_id, '+-'.encode('utf8')).decode('utf8')
            print("BINARY")
        except:
            container_id = 'entity_' + base64.b64encode(entity_id.encode('utf8'), '+-'.encode('utf8')).decode('utf8')
        print("OUT->" + container_id)
    else:
        container_id = 'entity_' + str(entity_id)
    track_id = 'track_' + str(track_type)
    # TODO: Historical formatting, keep it?
    clean_values = {value['date'] if isinstance(value['date'], str) else value['date'].strftime('%Y-%m-%d'): value['value'] for value in values}
    f_client = FStoryClient(source_key)
    f_client.request({'command': 'set' if clean else 'update', 'collection_name': container_id, 'element_id': track_id, 'data': clean_values})
    LOGGER.info('Track content stored as ' + container_id + '.' + track_id + ' with ' + str(len(values)) + (' updated' if not clean else '') + ' elements.')
    new_values = get_track_content(source_key, entity_id, track_type)
    return new_values
