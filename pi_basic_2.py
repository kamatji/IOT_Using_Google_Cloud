#!/usr/bin/python


import datetime
import time
import jwt
import paho.mqtt.client as mqtt
import re


# Define some project-based variables to be used below. This should be the only
# block of variables that you need to edit in order to run this script

ssl_private_key_filepath = '/home/pi/demo_private.pem'
ssl_algorithm = 'RS256' # Either RS256 or ES256
root_cert_filepath = '/home/pi/roots.pem' # choose your owm path for the roots folder
project_id = '**************'   #project id in gcp
gcp_location = 'us-central1'  # select your owm cloud region as selected in registry
registry_id = '****'   # nmae of registry
device_id = '*****' # nmae of device in gcp

# end of user-variables

cur_time = datetime.datetime.utcnow()

def create_jwt():
  token = {
      'iat': cur_time,
      'exp': cur_time + datetime.timedelta(minutes=60),
      'aud': project_id
  }

  with open(ssl_private_key_filepath, 'r') as f:
    private_key = f.read()

  return jwt.encode(token, private_key, ssl_algorithm)

_CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, gcp_location, registry_id, device_id)
_MQTT_TELEMETRY_TOPIC = '/devices/{}/events'.format(device_id)
_MQTT_CONFIG_TOPIC = '/devices/{}/config'.format(device_id)
_MQTT_COMMANDS_TOPIC = '/devices/{}/commands/#'.format(device_id)

client = mqtt.Client(client_id=_CLIENT_ID)
# authorization is handled purely with JWT, no user/pass, so username can be whatever
client.username_pw_set(
    username='unused',
    password=create_jwt())

regExp = re.compile('1')


def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))

def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')

# I have seen, occasionally, some noise come through that needs to be stripped out
# This code ensures that it's stripped out properly
def message_text(orig):
    print ('matching message text: {}'.format(orig))
    ma = re.match(r'^b\'(.*)\'$', orig)
    if ma == None:
        return orig
    else:
        return ma.group(1)

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])


# Method which handles parsing the text message coming back from the Cloud
# This is where you could add your own messages to play with different
# actions based on messages coming back from the Cloud
def respondToMsg(msg):
    if msg == "Left_turn":
        # code for arm to turn left
        print("turning left")
    elif msg == "right":
        #code for arm to turn right
        print("turning right")
    elif msg == "up":
        #code for arm up
        print("turning up")
    elif msg == "down":
        # code for turning down
        print("turning down")

    else:
        #set arm to original position
        print("original_position")

def on_message(unused_client, unused_userdata, message):
    payload = str(message.payload)
    print('Received message \'{}\' on topic \'{}\''.format(payload, message.topic))
    respondToMsg(message_text(payload))

client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

client.tls_set(ca_certs=root_cert_filepath) # Replace this with 3rd party cert if that was used when creating registry
client.connect('mqtt.googleapis.com', 8883)
client.subscribe(_MQTT_CONFIG_TOPIC, qos=1)
client.subscribe(_MQTT_COMMANDS_TOPIC, qos=1)
client.loop_start()





time.sleep(1)

# This is sleeping for an arbitrarily long time because it has to be connected
# in order to receive the command/config messages. Well, the config messages would
# come through next time the device connected, but that's not as interesting
# from a starting point
time.sleep(999)
client.loop_stop()
