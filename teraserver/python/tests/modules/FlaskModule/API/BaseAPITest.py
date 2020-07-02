import unittest
from requests import get, post, delete


class BaseAPITest(unittest.TestCase):
    host = 'localhost'
    port = 40075
    login_endpoint = ''
    test_endpoint = ''

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _request_with_http_auth(self, username, password, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return get(url=url, verify=False, auth=(username, password), params=payload)

    def _request_with_no_auth(self, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return get(url=url, verify=False, params=payload)

    def _post_with_http_auth(self, username, password, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return post(url=url, verify=False, auth=(username, password), json=payload)

    def _post_with_no_auth(self, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return post(url=url, verify=False, json=payload)

    def _delete_with_http_auth(self, username, password, id_to_del: int):
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return delete(url=url, verify=False, auth=(username, password), params='id=' + str(id_to_del))

    def _delete_with_no_auth(self, id_to_del: int):
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return delete(url=url, verify=False, params='id=' + str(id_to_del))