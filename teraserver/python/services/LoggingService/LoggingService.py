import services.LoggingService.Globals as Globals
from libtera.redis.RedisClient import RedisClient
from services.LoggingService.ConfigManager import ConfigManager
from services.shared.ServiceAccessManager import ServiceAccessManager
from modules.RedisVars import RedisVars
from modules.BaseModule import ModuleNames, create_module_message_topic_from_name, create_module_event_topic_from_name
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.message import DecodeError

# Twisted
from twisted.application import internet, service
from twisted.internet import reactor, ssl, defer
from twisted.python.threadpool import ThreadPool
from twisted.web.http import HTTPChannel
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.python import log
import messages.python as messages
import sys
import os
import uuid

from services.shared.ServiceOpenTera import ServiceOpenTera
from flask_babel import gettext


class LoggingService(ServiceOpenTera):
    def __init__(self, config_man: ConfigManager, this_service_info):
        ServiceOpenTera.__init__(self, config_man, this_service_info)

        # self.application = service.Application(self.config['name'])
        self.loglevel = messages.LogEvent.LOGLEVEL_TRACE

    def notify_service_messages(self, pattern, channel, message):
        pass

    @defer.inlineCallbacks
    def register_to_events(self):
        # Need to register to events produced by UserManagerModule
        ret1 = yield self.subscribe_pattern_with_callback('log.*', self.log_event_received)
        print(ret1)

    def log_event_received(self, pattern, channel, message):
        print('LoggingService - user_manager_event_received', pattern, channel, message)
        try:
            tera_event = messages.TeraEvent()
            if isinstance(message, str):
                ret = tera_event.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                ret = tera_event.ParseFromString(message)

            log_event = messages.LogEvent()

            # Look for UserEvent, ParticipantEvent, DeviceEvent
            for any_msg in tera_event.events:
                if any_msg.Unpack(log_event):
                    print(log_event)

        except DecodeError as d:
            print('LoggingService - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('LoggingService - Failure in redisMessageReceived', e)

    def setup_rpc_interface(self):
        # TODO Update rpc interface
        self.rpc_api['set_loglevel'] = {'args': ['str:loglevel'],
                                          'returns': 'dict',
                                          'callback': self.set_loglevel}

    def set_loglevel(self, loglevel):
        pass


if __name__ == '__main__':

    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    # Load configuration
    if not Globals.config_man.load_config('LoggingService.json'):
        print('Invalid config')
        exit(1)

    # Global redis client
    Globals.redis_client = RedisClient(Globals.config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    Globals.api_device_static_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceStaticTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)
    Globals.api_participant_static_token_key = \
        Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantStaticTokenAPIKey)

    # Update Service Access information
    ServiceAccessManager.api_user_token_key = Globals.api_user_token_key
    ServiceAccessManager.api_participant_token_key = Globals.api_participant_token_key
    ServiceAccessManager.api_participant_static_token_key = Globals.api_participant_static_token_key
    ServiceAccessManager.api_device_token_key = Globals.api_device_token_key
    ServiceAccessManager.api_device_static_token_key = Globals.api_device_static_token_key
    ServiceAccessManager.config_man = Globals.config_man

    # Get service UUID
    service_info = Globals.redis_client.redisGet(RedisVars.RedisVar_ServicePrefixKey +
                                                 Globals.config_man.service_config['name'])
    import sys
    if service_info is None:
        sys.stderr.write('Error: Unable to get service info from OpenTera Server - is the server running and config '
                         'correctly set in this service?')
        exit(1)
    import json
    service_info = json.loads(service_info)
    if 'service_uuid' not in service_info:
        sys.stderr.write('OpenTera Server didn\'t return a valid service UUID - aborting.')
        exit(1)

    # Update service uuid
    Globals.config_man.service_config['ServiceUUID'] = service_info['service_uuid']

    # Update port, hostname, endpoint
    Globals.config_man.service_config['port'] = service_info['service_port']
    Globals.config_man.service_config['hostname'] = service_info['service_hostname']

    # Create the Service
    service = LoggingService(Globals.config_man, service_info)

    # Start App / reactor events
    reactor.run()