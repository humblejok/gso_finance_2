'''
Created on 30 janv. 2018

@author: sdejo
'''

from json import loads, dumps

import pika
import uuid
import logging
import time
import bson

DATA_QUEUE = 'VPBANK_PROVIDER'

BROKER_URL = 'amqp://providers:providers@localhost:5672/providers'

SOURCES = {'finance': {'url': 'amqp://providers:providers@localhost:5672/providers', 'queue': 'FINANCE_PROVIDER'},
           'vpbank': {'url': 'amqp://providers:providers@localhost:5672/providers', 'queue': 'VPBANK_PROVIDER'}}

LOGGER = logging.getLogger(__name__)

class FStoryClient(object):
    
    connection = None
    channel = None
    response_queue = None
    correlation_id = None
    response = None
    
    source_key = 'finance'
        
    def __init__(self, source_key='finance'):
        self.source_key = source_key
        self.connect()
        
    def connect(self):
        connected = False
        while not connected:
            try:
                self.connection = pika.BlockingConnection(pika.URLParameters(SOURCES[self.source_key]['url']))
                connected = True
            except:
                time.sleep(0.01)
        self.channel = self.connection.channel()
        queue_declaration = self.channel.queue_declare(exclusive=True)
        self.response_queue =  queue_declaration.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.response_queue)
        
    def on_response(self, channel, method, header, body):
        if self.correlation_id==header.correlation_id:
            self.response = loads(body)
    
    def request(self, query):
        if self.connection.is_closed:
            self.connect()
        self.response = None
        self.correlation_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='', routing_key=SOURCES[self.source_key]['queue'], body=dumps(query), properties=pika.BasicProperties(correlation_id=self.correlation_id, reply_to=self.response_queue))
        try:
            while not self.response!=None:
                self.connection.process_data_events()
            return self.response['data'] if 'data' in self.response else None
        except pika.exceptions.AMQPError as e:
            LOGGER.debug("Connection " + str(self.connection) + " generates an error:" + str(e))
            

def get_track_content(source_key, entity_id, track_type, ascending = True, divisor = 1.0, substract = 0.0):
    if divisor==1.0 and substract==0.0 and ascending:
        f_client = FStoryClient(source_key)
        container_id = 'entity_' + str(entity_id)
        track_id = 'track_' + str(track_type)
        LOGGER.info('Loading track content of ' + container_id + ' - ' + track_id)
        raw_values = f_client.request({'command': 'ordered', 'collection_name': container_id, 'element_id': track_id})
        if raw_values!=None:
            LOGGER.info('Track content loaded from ' + container_id + '.' + track_id + ' with ' + str(len(raw_values)) + ' elements.')
            data = bson.BSON.encode({'content': raw_values})
        else:
            LOGGER.info('Track content loaded from ' + container_id + '.' + track_id + ' is EMPTY.')
            data = bson.BSON.encode({'content': []})
        
        return bson.BSON.decode(data)['content'] if data!=None else []
    else:
        container_id = 'entity_' + str(entity_id)
        track_id = 'track_' + str(track_type)
        raw_values = f_client.request({'command': 'ordered', 'collection_name': container_id, 'element_id': track_id})
        LOGGER.info('Track content loaded from ' + container_id + '.' + track_id + ' with ' + str(len(raw_values)) + ' elements.')
        data = [{'date':value['date'], 'value': (value[u'value']/divisor) - substract } for value in raw_values]
        # TODO: Implement ascending(true/false)
        return data

def clean_track_content(source_key, entity_id, track_type):
    entity_id = 'entity_' + str(entity_id)
    track_id = 'track_' + str(track_type)
    f_client = FStoryClient(source_key)
    f_client.request({'command': 'set', 'collection_name': entity_id, 'element_id': track_id, 'data': {}})

def set_track_content(source_key, entity_id, track_type, values, clean):
    LOGGER.info('Storing track content')
    entity_id = 'entity_' + str(entity_id)
    track_id = 'track_' + str(track_type)
    # TODO: Historical formatting, keep it?
    clean_values = {value['date'] if isinstance(value['date'], str) else value['date'].strftime('%Y-%m-%d'): value['value'] for value in values}
    f_client = FStoryClient(source_key)
    f_client.request({'command': 'set' if clean else 'update', 'collection_name': entity_id, 'element_id': track_id, 'data': clean_values})
    LOGGER.info('Track content stored as ' + entity_id + '.' + track_id + ' with ' + str(len(values)) + (' updated' if not clean else '') + ' elements.')
    values = get_track_content(entity_id, track_type)
