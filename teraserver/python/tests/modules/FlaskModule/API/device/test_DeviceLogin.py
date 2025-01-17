from BaseDeviceAPITest import BaseDeviceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice


class DeviceLoginTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/login'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import device_api_ns
        from BaseDeviceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.device.DeviceLogin import DeviceLogin
        kwargs = {
            'flaskModule': FakeFlaskModule(config=BaseDeviceAPITest.getConfig()),
            'test': True
        }
        device_api_ns.add_resource(DeviceLogin, '/login', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        response = self.test_client.get(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        response = self._get_with_device_token_auth(self.test_client, token='invalid')
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth(self):
        devices = []
        # Warning, device is updated on login, ORM will render the object "dirty".
        for device in TeraDevice.query.all():
            devices.append(device.to_json(minimal=False))

        for device in devices:
            if device['device_token']:
                if device['device_enabled']:
                    response = self._get_with_device_token_auth(self.test_client, token=device['device_token'])
                    self.assertEqual(200, response.status_code)

                    self.assertTrue('device_info' in response.json)
                    self.assertTrue('participants_info' in response.json)
                    self.assertTrue('session_types_info' in response.json)
                    self.assertEqual(device['id_device'], response.json['device_info']['id_device'])

                    if device['device_onlineable']:
                        self.assertTrue('websocket_url' in response.json)

                else:
                    response = self._get_with_device_token_auth(self.test_client, token=device['device_token'])
                    self.assertEqual(401, response.status_code)
