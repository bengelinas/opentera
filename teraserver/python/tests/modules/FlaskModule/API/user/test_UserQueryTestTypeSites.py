from BaseUserAPITest import BaseUserAPITest
from modules.FlaskModule.FlaskModule import flask_app


class UserQuerySessionTypeSitesTest(BaseUserAPITest):
    test_endpoint = '/api/user/testtypes/sites'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import user_api_ns
        from BaseUserAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.user.UserQueryTestTypeSites import UserQueryTestTypeSites
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseUserAPITest.getConfig())}
        user_api_ns.add_resource(UserQueryTestTypeSites, '/testtypes/sites', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        response = self._get_with_user_http_auth(client=self.test_client)
        self.assertEqual(response.status_code, 401)

    def test_post_no_auth(self):
        response = self._post_with_user_http_auth(client=self.test_client)
        self.assertEqual(response.status_code, 401)

    def test_delete_no_auth(self):
        response = self._delete_with_user_http_auth(client=self.test_client)
        self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        response = self._get_with_user_http_auth(username='admin', password='admin', client=self.test_client)
        self.assertEqual(response.status_code, 400)

    def test_query_as_user(self):
        response = self._get_with_user_http_auth(username='user', password='user', params="", client=self.test_client)
        self.assertEqual(response.status_code, 400)

    def test_query_site_as_admin(self):
        params = {'id_site': 10}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 0)

        params = {'id_site': 2}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_site_with_test_types_as_admin(self):
        params = {'id_site': 1, 'with_test_types': 1}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_test_type_as_admin(self):
        params = {'id_test_type': 30}  # Invalid
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 0)

        params = {'id_test_type': 1}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_test_type_with_site_as_admin(self):
        params = {'id_test_type': 3, 'with_sites': 1}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_list_as_admin(self):
        params = {'id_site': 1, 'list': 1}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_site_as_user(self):
        params = {'id_site': 2}
        response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 0)

        params = {'id_site': 1}
        response = self._get_with_user_http_auth(username='user4', password='user4', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 0)

        params = {'id_site': 1}
        response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_site_with_test_types_as_user(self):
        params = {'id_site': 1, 'with_test_types': 1}
        response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_test_type_as_user(self):
        params = {'id_test_type': 30}  # Invalid
        response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 0)

        params = {'id_test_type': 4}
        response = self._get_with_user_http_auth(username='user4', password='user4', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 0)

        params = {'id_test_type': 2}
        response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_test_type_with_sites_as_user(self):
        params = {'id_test_type': 1, 'with_sites': 1}
        response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        params = {'id_test_type': 1, 'list': 1}

        response = self._get_with_user_http_auth(username='user4', password='user4', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 0)

        response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_post_test_type(self):
        # New with minimal infos
        json_data = {}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 400, msg="Missing everything")  # Missing

        # Update
        json_data = {'test_type': {}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 400, msg="Missing id_test_type")

        json_data = {'test_type': {'id_test_type': 4}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 400, msg="Missing sites")

        json_data = {'test_type': {'id_test_type': 1, 'sites': []}}
        response = self._post_with_user_http_auth(username='user', password='user', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

        response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Remove from all accessible sites OK")

        params = {'id_test_type': 1}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 1)  # One should remain in the "top secret" site

        json_data = {'test_type': {'id_test_type': 1, 'sites': []}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Remove from all accessible sites OK")

        params = {'id_test_type': 1}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 0)  # None remaining now

        json_data = {'test_type': {'id_test_type': 1, 'sites': [{'id_site': 1},
                                                                {'id_site': 2}]}}
        response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 403, msg="No access to site 2")

        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="All posted ok")

        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 2)  # Everything was added

        json_data = {'test_type': {'id_test_type': 1, 'sites': [{'id_site': 1}]}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Remove one site")

        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 1)

        json_data = {'test_type': {'id_test_type': 1, 'sites': [{'id_site': 1},
                                                                {'id_site': 2}]}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Add all sites OK")

        # Recreate default associations - projects
        # Not useful in current test structure
        # json_data = {'test_type_project': [{'id_test_type': 1, 'id_project': 1}]}
        # response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
        #                                           client=self.test_client, endpoint='/api/user/testtypes/projects')
        # self.assertEqual(response.status_code, 200)

    def test_post_site(self):
        # Site update
        json_data = {'site': {}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 400, msg="Missing id_site")

        json_data = {'site': {'id_site': 1}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 400, msg="Missing services")

        json_data = {'site': {'id_site': 1, 'testtypes': []}}
        response = self._post_with_user_http_auth(username='user', password='user', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

        response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Remove all services OK")

        params = {'id_site': 1}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 0)  # Everything was deleted!

        json_data = {'site': {'id_site': 1, 'testtypes': [{'id_test_type': 1},
                                                          {'id_test_type': 2}
                                                          ]}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Add all test types OK")

        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 2)  # Everything was added

        json_data = {'site': {'id_site': 1, 'testtypes': [{'id_test_type': 2}]}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Remove 1 test type")

        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 1)

        json_data = {'site': {'id_site': 1, 'testtypes': [{'id_test_type': 1},
                                                          {'id_test_type': 2}
                                                          ]}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Back to defaults")

        # Recreate default associations - projects
        # Not useful in current test structure
        # json_data = {'test_type_project': [{'id_test_type': 1, 'id_project': 1},
        #                                    {'id_test_type': 2, 'id_project': 1}
        #                                    ]}
        # response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
        #                                           client=self.test_client, endpoint='/api/user/testtypes/projects')
        # self.assertEqual(response.status_code, 200)

    def test_post_test_type_site_and_delete(self):
        json_data = {'test_type_site': {}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 400, msg="Badly formatted request")

        json_data = {'test_type_site': {'id_site': 2}}
        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 400, msg="Badly formatted request")

        json_data = {'test_type_site': {'id_site': 2, 'id_test_type': 2}}
        response = self._post_with_user_http_auth(username='user', password='user', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

        response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 403, msg="Not site admin either for that site")

        response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                  client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Add new association OK")

        params = {'id_site': 2}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 3)

        current_id = None
        for sp in json_data:
            if sp['id_test_type'] == 2:
                current_id = sp['id_test_type_site']
                break
        self.assertFalse(current_id is None)

        response = self._delete_with_user_http_auth(username='user', password='user', params='id=' + str(current_id),
                                                    client=self.test_client)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_user_http_auth(username='siteadmin', password='siteadmin',
                                                    params='id=' + str(current_id), client=self.test_client)
        self.assertEqual(response.status_code, 403, msg="Delete still denied")

        response = self._delete_with_user_http_auth(username='admin', password='admin', params='id=' + str(current_id),
                                                    client=self.test_client)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

        params = {'id_site': 2}
        response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                 client=self.test_client)
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 2)  # Back to initial state!

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_test_type_site'))
        self.assertTrue(json_data.__contains__('id_test_type'))
        self.assertTrue(json_data.__contains__('id_site'))

        if not minimal:
            self.assertTrue(json_data.__contains__('test_type_name'))
            self.assertTrue(json_data.__contains__('site_name'))
        else:
            self.assertFalse(json_data.__contains__('test_type_name'))
            self.assertFalse(json_data.__contains__('site_name'))
