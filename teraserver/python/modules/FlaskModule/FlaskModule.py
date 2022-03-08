from flask import Flask, request, g, url_for
from flask_session import Session
from flask_restx import Api
from opentera.config.ConfigManager import ConfigManager
from flask_babel import Babel
from opentera.modules.BaseModule import BaseModule, ModuleNames
from opentera.db.models.TeraServerSettings import TeraServerSettings
import redis

# Flask application
flask_app = Flask("TeraServer")

# Translations
babel = Babel(flask_app)

# API
authorizations = {
    'HTTPAuth': {
        'type': 'basic',
        'in': 'header'
    },
    'Token Authentication': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'default': 'OpenTera',
        'bearerFormat': 'JWT'
    }
}


# Simple fix for API documentation used with reverse proxy
class CustomAPI(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)


api = CustomAPI(flask_app, version='1.0.0', title='OpenTeraServer API',
                description='TeraServer API Documentation', doc='/doc', prefix='/api',
                authorizations=authorizations)

# Namespaces
user_api_ns = api.namespace('user', description='API for user calls')
device_api_ns = api.namespace('device', description='API for device calls')
participant_api_ns = api.namespace('participant', description='API for participant calls')
service_api_ns = api.namespace('service', description='API for service calls')


@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support fr/en in this
    # example.  The best match wins.
    lang = request.accept_languages.best_match(['fr', 'en'])
    return lang


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


class FlaskModule(BaseModule):

    def __init__(self,  config: ConfigManager):

        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)

        # Use debug mode flag
        flask_app.debug = config.server_config['debug_mode']
        # flask_app.secret_key = 'development'
        # Change secret key to use server UUID
        # This is used for session encryption
        flask_app.secret_key = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)

        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})
        # TODO set upload folder in config
        # TODO remove this configuration, it is not useful?
        flask_app.config.update({'UPLOAD_FOLDER': 'uploads'})

        # Not sure.
        # flask_app.config.update({'BABEL_DEFAULT_TIMEZONE': 'UTC'})

        self.session = Session(flask_app)

        # Init API
        self.init_user_api()
        self.init_device_api()
        self.init_participant_api()
        self.init_service_api()

        # Init Views
        self.init_views()

    def setup_module_pubsub(self):
        # Additional subscribe
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('FlaskModule - Received message ', pattern, channel, message)
        pass

    def init_user_api(self):

        # Default arguments
        kwargs = {'flaskModule': self}

        # Users...
        from modules.FlaskModule.API.user.UserLogin import UserLogin
        from modules.FlaskModule.API.user.UserLogout import UserLogout
        from modules.FlaskModule.API.user.UserQueryUsers import UserQueryUsers
        from modules.FlaskModule.API.user.UserQueryUserPreferences import UserQueryUserPreferences
        from modules.FlaskModule.API.user.UserQueryUserGroups import UserQueryUserGroups
        from modules.FlaskModule.API.user.UserQueryForms import UserQueryForms
        from modules.FlaskModule.API.user.UserQueryOnlineUsers import UserQueryOnlineUsers
        from modules.FlaskModule.API.user.UserQueryOnlineParticipants import UserQueryOnlineParticipants
        from modules.FlaskModule.API.user.UserQueryOnlineDevices import UserQueryOnlineDevices
        from modules.FlaskModule.API.user.UserQuerySites import UserQuerySites
        from modules.FlaskModule.API.user.UserQueryProjects import UserQueryProjects
        from modules.FlaskModule.API.user.UserQueryParticipants import UserQueryParticipants
        from modules.FlaskModule.API.user.UserQueryDevices import UserQueryDevices
        from modules.FlaskModule.API.user.UserQuerySiteAccess import UserQuerySiteAccess
        from modules.FlaskModule.API.user.UserQueryDeviceSites import UserQueryDeviceSites
        from modules.FlaskModule.API.user.UserQueryDeviceProjects import UserQueryDeviceProjects
        from modules.FlaskModule.API.user.UserQueryDeviceParticipants import UserQueryDeviceParticipants
        from modules.FlaskModule.API.user.UserQueryProjectAccess import UserQueryProjectAccess
        from modules.FlaskModule.API.user.UserQueryParticipantGroup import UserQueryParticipantGroup
        from modules.FlaskModule.API.user.UserQuerySessions import UserQuerySessions
        from modules.FlaskModule.API.user.UserQuerySessionTypes import UserQuerySessionTypes
        from modules.FlaskModule.API.user.UserQuerySessionEvents import UserQuerySessionEvents
        from modules.FlaskModule.API.user.UserQuerySessionTypeSites import UserQuerySessionTypeSites
        from modules.FlaskModule.API.user.UserQuerySessionTypeProjects import UserQuerySessionTypeProjects
        from modules.FlaskModule.API.user.UserQueryDeviceTypes import UserQueryDeviceTypes
        from modules.FlaskModule.API.user.UserQueryDeviceSubTypes import UserQueryDeviceSubTypes
        from modules.FlaskModule.API.user.UserQueryAssets import UserQueryAssets
        from modules.FlaskModule.API.user.UserQueryServices import UserQueryServices
        from modules.FlaskModule.API.user.UserQueryServiceProjects import UserQueryServiceProjects
        from modules.FlaskModule.API.user.UserQueryServiceSites import UserQueryServiceSites
        from modules.FlaskModule.API.user.UserQueryServiceAccess import UserQueryServiceAccess
        from modules.FlaskModule.API.user.UserSessionManager import UserSessionManager
        from modules.FlaskModule.API.user.UserQueryServiceConfigs import UserQueryServiceConfig
        from modules.FlaskModule.API.user.UserQueryStats import UserQueryUserStats
        from modules.FlaskModule.API.user.UserQueryUserUserGroups import UserQueryUserUserGroups
        from modules.FlaskModule.API.user.UserRefreshToken import UserRefreshToken
        from modules.FlaskModule.API.user.UserQueryVersions import UserQueryVersions
        # Resources
        user_api_ns.add_resource(UserLogin,                 '/login', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserLogout,                '/logout', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySites,            '/sites', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUsers,            '/users', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryOnlineUsers,      '/users/online', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUserGroups,       '/usergroups', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUserUserGroups,   '/users/usergroups', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUserPreferences,  '/users/preferences', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryForms,            '/forms', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryProjects,         '/projects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryParticipants,     '/participants', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryOnlineParticipants, '/participants/online', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDevices,          '/devices', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryOnlineDevices,    '/devices/online', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceSites,      '/devicesites', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceSites,      '/device/sites', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceProjects,   '/deviceprojects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceProjects,   '/device/projects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceParticipants, '/deviceparticipants', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceParticipants, '/device/participants', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySiteAccess,       '/siteaccess', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryProjectAccess,    '/projectaccess', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryParticipantGroup, '/groups', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessions,         '/sessions', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserSessionManager,        '/sessions/manager', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessionTypes,     '/sessiontypes', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessionTypeProjects, '/sessiontypeprojects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessionTypeProjects, '/sessiontypes/projects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessionTypeSites, '/sessiontypes/sites', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQuerySessionEvents,    '/sessions/events', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceTypes,      '/devicetypes', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryDeviceSubTypes,   '/devicesubtypes', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryAssets,           '/assets', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryServices,         '/services', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryServiceProjects,  '/services/projects', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryServiceSites,     '/services/sites', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryServiceAccess,    '/services/access', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryServiceConfig,    '/services/configs', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryUserStats,        '/stats', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserRefreshToken,          '/refresh_token', resource_class_kwargs=kwargs)
        user_api_ns.add_resource(UserQueryVersions,         '/versions', resource_class_kwargs=kwargs)
        api.add_namespace(user_api_ns)

    def init_device_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}

        # Devices
        from modules.FlaskModule.API.device.DeviceLogin import DeviceLogin
        from modules.FlaskModule.API.device.DeviceLogout import DeviceLogout
        from modules.FlaskModule.API.device.DeviceRegister import DeviceRegister
        from modules.FlaskModule.API.device.DeviceQuerySessions import DeviceQuerySessions
        from modules.FlaskModule.API.device.DeviceQuerySessionEvents import DeviceQuerySessionEvents
        from modules.FlaskModule.API.device.DeviceQueryDevices import DeviceQueryDevices
        from modules.FlaskModule.API.device.DeviceQueryAssets import DeviceQueryAssets
        from modules.FlaskModule.API.device.DeviceQueryParticipants import DeviceQueryParticipants
        from modules.FlaskModule.API.device.DeviceQueryStatus import DeviceQueryStatus

        # Resources
        device_api_ns.add_resource(DeviceLogin,                 '/login', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceLogout,                '/logout', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceRegister,              '/register', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQuerySessions,         '/sessions', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQuerySessionEvents,    '/sessions/events', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQueryDevices,          '/devices', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQueryAssets,           '/assets', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQueryParticipants,     '/participants', resource_class_kwargs=kwargs)
        device_api_ns.add_resource(DeviceQueryStatus,           '/status', resource_class_kwargs=kwargs)

        # Finally, add namespace
        api.add_namespace(device_api_ns)

    def init_participant_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}

        # Participants
        from modules.FlaskModule.API.participant.ParticipantLogin import ParticipantLogin
        from modules.FlaskModule.API.participant.ParticipantLogout import ParticipantLogout
        from modules.FlaskModule.API.participant.ParticipantQueryDevices import ParticipantQueryDevices
        from modules.FlaskModule.API.participant.ParticipantQueryParticipants import ParticipantQueryParticipants
        from modules.FlaskModule.API.participant.ParticipantQuerySessions import ParticipantQuerySessions
        from modules.FlaskModule.API.participant.ParticipantRefreshToken import ParticipantRefreshToken
        from modules.FlaskModule.API.participant.ParticipantQueryAssets import ParticipantQueryAssets
        # Resources
        participant_api_ns.add_resource(ParticipantLogin,               '/login', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantLogout,              '/logout', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantQueryAssets,         '/assets', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantQueryDevices,        '/devices', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantQueryParticipants,   '/participants', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantQuerySessions,       '/sessions', resource_class_kwargs=kwargs)
        participant_api_ns.add_resource(ParticipantRefreshToken,        '/refresh_token', resource_class_kwargs=kwargs)

        api.add_namespace(participant_api_ns)

    def init_service_api(self):
        # Default arguments
        kwargs = {'flaskModule': self}

        # Services
        from modules.FlaskModule.API.service.ServiceQueryParticipants import ServiceQueryParticipants
        from modules.FlaskModule.API.service.ServiceQueryAssets import ServiceQueryAssets
        from modules.FlaskModule.API.service.ServiceQuerySessions import ServiceQuerySessions
        from modules.FlaskModule.API.service.ServiceQuerySessionEvents import ServiceQuerySessionEvents
        from modules.FlaskModule.API.service.ServiceQuerySiteProjectAccessRoles import ServiceQuerySiteProjectAccessRoles
        from modules.FlaskModule.API.service.ServiceQueryUsers import ServiceQueryUsers
        from modules.FlaskModule.API.service.ServiceQueryServices import ServiceQueryServices
        from modules.FlaskModule.API.service.ServiceQueryProjects import ServiceQueryProjects
        from modules.FlaskModule.API.service.ServiceQuerySites import ServiceQuerySites
        from modules.FlaskModule.API.service.ServiceSessionManager import ServiceSessionManager
        from modules.FlaskModule.API.service.ServiceQuerySessionTypes import ServiceQuerySessionTypes
        from modules.FlaskModule.API.service.ServiceQueryDevices import ServiceQueryDevices

        service_api_ns.add_resource(ServiceQueryUsers, '/users', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQueryParticipants,   '/participants', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQueryDevices, '/devices', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQueryAssets,         '/assets', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQuerySessions,       '/sessions', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQuerySessionEvents,  '/sessions/events', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQuerySiteProjectAccessRoles, '/users/access', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQueryServices,       '/services', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQueryProjects,       '/projects', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQuerySites,          '/sites', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceSessionManager,      '/sessions/manager', resource_class_kwargs=kwargs)
        service_api_ns.add_resource(ServiceQuerySessionTypes,   '/sessiontypes', resource_class_kwargs=kwargs)

        # Add namespace
        api.add_namespace(service_api_ns)

    def init_views(self):
        from modules.FlaskModule.Views.About import About

        # Default arguments
        args = []
        kwargs = {'flaskModule': self}

        # About
        flask_app.add_url_rule('/about', view_func=About.as_view('about', *args, **kwargs))


@flask_app.after_request
def apply_caching(response):
    # This is required to expose the backend API to rendered webpages from other sources, such as services
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"

    # Request processing time
    import time
    print(f"Process time: {(time.time() - g.start_time)*1000} ms")
    return response


@flask_app.before_request
def compute_request_time():
    import time
    g.start_time = time.time()
