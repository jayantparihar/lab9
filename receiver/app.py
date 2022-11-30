import logging
from types import new_class
import uuid
import connexion
import json
import datetime
from connexion import NoContent
import os
from swagger_ui_bundle import swagger_ui_path
import requests
import yaml
import logging
import logging.config
import random
from pykafka import KafkaClient
import time



with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def generate_trace_id():
    # trace_id = random.randint(1,99999999999) 
    trace_id = str(uuid.uuid4())
    return trace_id

current_retrive = 0
max_retrive =20
time_in_seconds=5
while current_retrive < max_retrive:
    try:
        host = str(app_config['events']['hostname'])+":"+ str(app_config['events']['port'])
        headers = { 'content-type': 'application/json' }
        client = KafkaClient(hosts=host)
        topic = client.topics[str.encode(app_config['events']['topic'])]
        producer = topic.get_sync_producer()
        break
    except:
        print("Connection for kafka failed")
        time.sleep(time_in_seconds)
        current_retrive+=1



def report_ph_level(body):  

    traceid =  generate_trace_id()
    body["trace_id"] = traceid
    logger.info("Received event PH level request with a unique id of %s"%body["trace_id"] )
    msg = { "type": "ph_level",
        "datetime" :
        datetime.datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%S"),
        "payload": body }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201


def report_chlorine_level(body):
    traceid =  generate_trace_id()
    body["trace_id"] = traceid
    logger.info("Received event Chlorine level request with a unique id of %s"%body["trace_id"] )
    logger.debug(body)
    msg = { "type": "chlorine_level",
        "datetime" :
        datetime.datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%S"),
        "payload": body }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.debug(msg_str)
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
        strict_validation=True,
        validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
