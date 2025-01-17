from services.FileTransferService.FlaskModule import flask_app
import services.FileTransferService.Globals as Globals
from opentera.redis.RedisClient import RedisClient
from services.FileTransferService.ConfigManager import ConfigManager
from opentera.services.ServiceAccessManager import ServiceAccessManager
from opentera.redis.RedisVars import RedisVars

# Twisted
from twisted.internet import reactor, defer
from twisted.python import log
import sys
import os

from opentera.services.ServiceOpenTeraWithAssets import ServiceOpenTeraWithAssets
from sqlalchemy.exc import OperationalError
from services.FileTransferService.FlaskModule import FlaskModule
import opentera.messages.python as messages


class FileTransferService(ServiceOpenTeraWithAssets):
    def __init__(self, config_man: ConfigManager, this_service_info):
        ServiceOpenTeraWithAssets.__init__(self, config_man, this_service_info)

        self.verify_file_upload_directory(config_man)

        # Create REST backend
        self.flaskModule = FlaskModule(config_man)

        # Create twisted service
        self.flaskModuleService = self.flaskModule.create_service()

        # self.application = service.Application(self.config['name'])

    def verify_file_upload_directory(self, config: ConfigManager, create=True):
        file_upload_path = config.filetransfer_config['files_directory']

        if not os.path.exists(file_upload_path):
            if create:
                # TODO Change permissions?
                os.mkdir(file_upload_path, 0o700)
            else:
                return None
        return file_upload_path

    def notify_service_messages(self, pattern, channel, message):
        pass

    # @defer.inlineCallbacks
    def register_to_events(self):
        super().register_to_events()

    def asset_event_received(self, event: messages.DatabaseEvent):
        if event.object_type == 'asset':
            if event.type == messages.DatabaseEvent.DB_DELETE:
                print("FileTransfer Service - Delete Asset Event")
                asset_info = json.loads(event.object_value)
                from services.FileTransferService.libfiletransferservice.db.models.AssetFileData import AssetFileData
                asset = AssetFileData.get_asset_for_uuid(asset_info['asset_uuid'])
                if asset:
                    flask_app.app_context().push()
                    asset.delete_file_asset(flask_app.config['UPLOAD_FOLDER'])


if __name__ == '__main__':
    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    import argparse
    parser = argparse.ArgumentParser(description='FileTransfer Service')
    parser.add_argument('--enable_tests', help='Test mode for service.', default=False)
    args = parser.parse_args()

    # Load configuration
    if not Globals.config_man.load_config('FileTransferService.json'):
        print('Invalid config')
        exit(1)

    # Global redis client
    Globals.redis_client = RedisClient(Globals.config_man.redis_config)

    # Update Service Access information
    # ServiceAccessManager.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    #
    # ServiceAccessManager.api_participant_token_key = \
    #     Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)
    #
    # ServiceAccessManager.api_participant_static_token_key = \
    #     Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantStaticTokenAPIKey)
    #
    # ServiceAccessManager.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    #
    # ServiceAccessManager.api_device_static_token_key = \
    #     Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceStaticTokenAPIKey)
    #
    # ServiceAccessManager.api_service_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
    #
    # ServiceAccessManager.config_man = Globals.config_man

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

    # DATABASE CONFIG AND OPENING
    #############################
    POSTGRES = {
        'user': Globals.config_man.db_config['username'],
        'pw': Globals.config_man.db_config['password'],
        'db': Globals.config_man.db_config['name'],
        'host': Globals.config_man.db_config['url'],
        'port': Globals.config_man.db_config['port']
    }

    try:
        if args.enable_tests:
            Globals.db_man.open_local(None, echo=True)
        else:
            Globals.db_man.open(POSTGRES, Globals.config_man.service_config['debug_mode'])
    except OperationalError as e:
        print("Unable to connect to database - please check settings in config file!", e)
        quit()

    with flask_app.app_context():
        Globals.db_man.create_defaults(Globals.config_man)

    # Create the Service
    Globals.service = FileTransferService(Globals.config_man, service_info)

    # Start App / reactor events
    reactor.run()
