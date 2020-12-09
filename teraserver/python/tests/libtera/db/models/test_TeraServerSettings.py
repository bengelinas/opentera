import unittest
import os

from modules.DatabaseModule.DBManager import DBManager
from libtera.db.models.TeraServerSettings import TeraServerSettings

from libtera.db.models.TeraUser import TeraUser
from libtera.ConfigManager import ConfigManager


class TeraServerSettingsTest(unittest.TestCase):

    filename = os.path.join(os.path.dirname(__file__), 'TeraServerSettingsTest.db')

    SQLITE = {
        'filename': filename
    }

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.admin_user = None
        self.test_user = None

        self.config = ConfigManager()
        self.config.create_defaults()

        self.db_man = DBManager(self.config)

        self.db_man.open_local(self.SQLITE)

        # Creating default users / tests.
        self.db_man.create_defaults(self.config)

    def tearDown(self):
        pass

    def test_constants_check(self):
        for settings in TeraServerSettings.query.all():
            self.assertGreater(settings.id_server_settings, 0)
            self.assertIsNotNone(settings.server_settings_name)
            self.assertIsNotNone(settings.server_settings_value)
            self.assertEqual(settings.ServerDeviceTokenKey, 'TokenEncryptionKey')
            self.assertEqual(settings.ServerParticipantTokenKey, 'ParticipantTokenEncryptionKey')
            self.assertEqual(settings.ServerUUID, 'ServerUUID')
            self.assertEqual(settings.ServerVersions, 'ServerVersions')

    def test_set_and_get_settings(self):
        # test the get/set methods and the unique name
        TeraServerSettings.set_server_setting(setting_name='Nom Unique', setting_value='Key')
        new_settings = TeraServerSettings.get_server_setting(setting_name='Nom Unique')
        self.assertEqual(new_settings.server_settings_name, 'Nom Unique')
        self.assertEqual(new_settings.server_settings_value, 'Key')
        TeraServerSettings.set_server_setting(setting_name='Nom Unique', setting_value='Updated Key')
        new_settings2 = TeraServerSettings.get_server_setting(setting_name='Nom Unique')
        self.assertEqual(new_settings.server_settings_name, 'Nom Unique')
        self.assertEqual(new_settings.server_settings_value, 'Updated Key')
        self.assertEqual(new_settings2.server_settings_name, 'Nom Unique')
        self.assertEqual(new_settings2.server_settings_value, 'Updated Key')

        # If you want to create another server setting with the same name, it changes the original settings

    def test_generate_token_key(self):
        key_len_16 = TeraServerSettings.generate_token_key(length=16)
        key_len_32 = TeraServerSettings.generate_token_key(length=32)
        self.assertEqual(16, len(key_len_16))
        self.assertEqual(32, len(key_len_32))

    def test_get_server_setting_value(self):
        TeraServerSettings.set_server_setting(setting_name='Nom Unique', setting_value='Key')
        new_settings = TeraServerSettings.get_server_setting(setting_name='Nom Unique')
        self.assertEqual(new_settings.server_settings_value, TeraServerSettings.get_server_setting_value(setting_name='Nom Unique'))