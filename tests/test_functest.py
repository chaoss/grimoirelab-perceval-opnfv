# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2019 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#     Quan Zhou <quan@bitergia.com>
#

import datetime
import unittest
import unittest.mock

import httpretty
import dateutil.tz

from perceval.backend import BackendCommandArgumentParser
from perceval.backends.opnfv.functest import (Functest,
                                              FunctestClient,
                                              FunctestCommand)
from perceval.utils import DEFAULT_DATETIME

from base import TestCaseBackendArchive


def read_file(filename, mode='r'):
    with open(filename, mode) as f:
        content = f.read()
    return content


FUNCTEST_URL = "http://example.com/"
FUNCTEST_API_URL = FUNCTEST_URL + 'api/v1/'
FUNCTEST_RESULTS_URL = FUNCTEST_API_URL + 'results'


def setup_http_server():
    """Setup a mock HTTP server"""

    page1 = read_file('data/functest/functest_results_page_1.json', 'rb')
    page2 = read_file('data/functest/functest_results_page_2.json', 'rb')
    empty_page = read_file('data/functest/functest_results_empty.json', 'rb')

    def request_callback(method, uri, headers):
        params = httpretty.last_request().querystring
        status = 200

        if params['from'][0] == '2020-01-01 00:00:00':
            body = empty_page
        elif ('page' in params and params['page'][0] == '1'):
            body = page1
        elif ('page' in params and params['page'][0] == '2'):
            body = page2
        else:
            raise

        return (status, headers, body)

    httpretty.register_uri(httpretty.GET,
                           FUNCTEST_RESULTS_URL,
                           responses=[
                               httpretty.Response(body=request_callback)
                           ])


class TestFunctestBackend(unittest.TestCase):
    """Functest backend tests"""

    def test_initialization(self):
        """Test whether attributes are initializated"""

        functest = Functest(FUNCTEST_URL, tag='test')

        self.assertEqual(functest.url, FUNCTEST_URL)
        self.assertEqual(functest.origin, FUNCTEST_URL)
        self.assertEqual(functest.tag, 'test')
        self.assertIsNone(functest.client)
        self.assertTrue(functest.ssl_verify)

        # When tag is empty or None it will be set to
        # the value in
        functest = Functest(FUNCTEST_URL, ssl_verify=False)
        self.assertEqual(functest.origin, FUNCTEST_URL)
        self.assertEqual(functest.tag, FUNCTEST_URL)
        self.assertFalse(functest.ssl_verify)

        functest = Functest(FUNCTEST_URL, tag='')
        self.assertEqual(functest.origin, FUNCTEST_URL)
        self.assertEqual(functest.tag, FUNCTEST_URL)

    def test_has_archiving(self):
        """Test if it returns True when has_archiving is called"""

        self.assertEqual(Functest.has_archiving(), True)

    def test_has_resuming(self):
        """Test if it returns False when has_resuming is called"""

        self.assertEqual(Functest.has_resuming(), False)

    @httpretty.activate
    @unittest.mock.patch('perceval.backends.opnfv.functest.datetime_utcnow')
    def test_fetch(self, mock_utcnow):
        """Test whether it fetches data from a repository"""

        mock_utcnow.return_value = datetime.datetime(2017, 6, 1, 11, 0, 0)

        setup_http_server()

        functest = Functest(FUNCTEST_URL)
        items = [item for item in functest.fetch(from_date=None, to_date=None)]

        self.assertEqual(len(items), 27)

        item = items[0]
        self.assertEqual(item['uuid'], '14d307c6511ad3e670a9b6cbef0942a4b5d09ab0')
        self.assertEqual(item['origin'], FUNCTEST_URL)
        self.assertEqual(item['updated_on'], 1496314767.0)
        self.assertEqual(item['category'], 'functest')
        self.assertEqual(item['tag'], FUNCTEST_URL)
        self.assertEqual(item['data']['_id'], '592ff62c78a2ad000ae6af4d')

        item = items[26]
        self.assertEqual(item['uuid'], 'cca9bf1e338b4cac4fbedf1d0cc46b2f36465e8c')
        self.assertEqual(item['origin'], FUNCTEST_URL)
        self.assertEqual(item['updated_on'], 1496311317.0)
        self.assertEqual(item['category'], 'functest')
        self.assertEqual(item['tag'], FUNCTEST_URL)
        self.assertEqual(item['data']['_id'], '592fe61678a2ad000ae6af33')

        # Check requests
        expected = [
            {
                'from': ['1970-01-01 00:00:00'],
                'to': ['2017-06-01 11:00:00'],
                'page': ['1']
            },
            {
                'from': ['1970-01-01 00:00:00'],
                'to': ['2017-06-01 11:00:00'],
                'page': ['2']
            }
        ]

        latest_requests = httpretty.httpretty.latest_requests
        self.assertEqual(len(latest_requests), 2)
        self.assertDictEqual(latest_requests[0].querystring, expected[0])
        self.assertDictEqual(latest_requests[1].querystring, expected[1])

    @httpretty.activate
    def test_fetch_from_date(self):
        """Test whether it fetches data from a repository using dates for filtering"""

        from_date = datetime.datetime(2017, 6, 1, 10, 0, 0)
        to_date = datetime.datetime(2017, 6, 1, 11, 0, 0)

        setup_http_server()

        functest = Functest(FUNCTEST_URL)
        items = [item for item in functest.fetch(from_date=from_date,
                                                 to_date=to_date)]

        self.assertEqual(len(items), 27)

        item = items[0]
        self.assertEqual(item['uuid'], '14d307c6511ad3e670a9b6cbef0942a4b5d09ab0')
        self.assertEqual(item['origin'], FUNCTEST_URL)
        self.assertEqual(item['updated_on'], 1496314767.0)
        self.assertEqual(item['category'], 'functest')
        self.assertEqual(item['tag'], FUNCTEST_URL)
        self.assertEqual(item['data']['_id'], '592ff62c78a2ad000ae6af4d')

        item = items[26]
        self.assertEqual(item['uuid'], 'cca9bf1e338b4cac4fbedf1d0cc46b2f36465e8c')
        self.assertEqual(item['origin'], FUNCTEST_URL)
        self.assertEqual(item['updated_on'], 1496311317.0)
        self.assertEqual(item['category'], 'functest')
        self.assertEqual(item['tag'], FUNCTEST_URL)
        self.assertEqual(item['data']['_id'], '592fe61678a2ad000ae6af33')

        # Check requests
        expected = [
            {
                'from': ['2017-06-01 10:00:00'],
                'to': ['2017-06-01 11:00:00'],
                'page': ['1']
            },
            {
                'from': ['2017-06-01 10:00:00'],
                'to': ['2017-06-01 11:00:00'],
                'page': ['2']
            }
        ]

        latest_requests = httpretty.httpretty.latest_requests
        self.assertEqual(len(latest_requests), 2)
        self.assertDictEqual(latest_requests[0].querystring, expected[0])
        self.assertDictEqual(latest_requests[1].querystring, expected[1])

    @httpretty.activate
    def test_fetch_empty(self):
        """Test whether it works when no data is returned"""

        setup_http_server()

        from_date = datetime.datetime(2020, 1, 1)

        functest = Functest(FUNCTEST_URL)
        items = [item for item in functest.fetch(from_date=from_date)]

        self.assertEqual(len(items), 0)

        # Check requests
        self.assertEqual(len(httpretty.httpretty.latest_requests), 1)

    @httpretty.activate
    def test_search_fields(self):
        """Test whether the search_fields is properly set"""

        setup_http_server()

        functest = Functest(FUNCTEST_URL)
        items = [item for item in functest.fetch()]

        item = items[0]
        self.assertEqual(functest.metadata_id(item['data']), item['search_fields']['item_id'])
        self.assertEqual(item['data']['project_name'], 'functest')
        self.assertEqual(item['data']['project_name'], item['search_fields']['project_name'])

    def test_parse_json(self):
        """Test if it parses a JSON stream"""

        raw_json = read_file('data/functest/functest_results.json')

        data = Functest.parse_json(raw_json)
        self.assertEqual(len(data), 27)


class TestFunctestBackendArchive(TestCaseBackendArchive):
    """Functest backend tests using an archive"""

    def setUp(self):
        super().setUp()
        self.backend_write_archive = Functest(FUNCTEST_URL, archive=self.archive)
        self.backend_read_archive = Functest(FUNCTEST_URL, archive=self.archive)

    @httpretty.activate
    @unittest.mock.patch('perceval.backends.opnfv.functest.datetime_utcnow')
    def test_fetch_from_archive(self, mock_utcnow):
        """Test whether it fetches data from a repository from archive"""

        mock_utcnow.return_value = datetime.datetime(2017, 6, 1, 11, 0, 0)

        setup_http_server()
        self._test_fetch_from_archive()

    @httpretty.activate
    def test_fetch_from_date_from_archive(self):
        """Test whether it fetches data from a repository using dates for filtering from archive"""

        from_date = datetime.datetime(2017, 6, 1, 10, 0, 0)
        to_date = datetime.datetime(2017, 6, 1, 11, 0, 0)

        setup_http_server()
        self._test_fetch_from_archive(from_date=from_date, to_date=to_date)

    @httpretty.activate
    def test_fetch_empty_from_archive(self):
        """Test whether it works when no data is returned from archive"""

        setup_http_server()
        from_date = datetime.datetime(2020, 1, 1)
        self._test_fetch_from_archive(from_date=from_date)


class TestFunctestClient(unittest.TestCase):
    """Functest API client tests.

    These tests do not check the body of the response, only if the call
    was well formed and if a response was obtained. Due to this, take
    into account that the body returned on each request might not
    match with the parameters from the request.
    """
    def test_init(self):
        """Test initialization"""

        functest = FunctestClient(FUNCTEST_URL)
        self.assertEqual(functest.base_url, FUNCTEST_URL)
        self.assertEqual(functest.max_retries, 3)
        self.assertIsNone(functest.archive)
        self.assertFalse(functest.from_archive)
        self.assertTrue(functest.ssl_verify)

        functest = FunctestClient(FUNCTEST_URL, ssl_verify=False)
        self.assertEqual(functest.base_url, FUNCTEST_URL)
        self.assertEqual(functest.max_retries, 3)
        self.assertIsNone(functest.archive)
        self.assertFalse(functest.from_archive)
        self.assertFalse(functest.ssl_verify)

    @httpretty.activate
    def test_repository(self):
        """Test repository API call"""

        # Set up a mock HTTP server
        setup_http_server()

        # Call API
        client = FunctestClient(FUNCTEST_URL)
        from_date = datetime.datetime(2017, 6, 1, 10, 0, 0)
        results = [r for r in client.results(from_date=from_date)]

        req = httpretty.last_request()

        expected = {
            'from': ['2017-06-01 10:00:00'],
            'page': ['2']
        }
        self.assertEqual(req.method, 'GET')
        self.assertRegex(req.path, '/api/v1/results')
        self.assertDictEqual(req.querystring, expected)

        # Test using to_date value
        to_date = datetime.datetime(2017, 6, 1, 11, 0, 0)
        results = [r for r in client.results(from_date=from_date, to_date=to_date)]

        req = httpretty.last_request()

        expected = {
            'from': ['2017-06-01 10:00:00'],
            'to': ['2017-06-01 11:00:00'],
            'page': ['2']
        }
        self.assertEqual(req.method, 'GET')
        self.assertRegex(req.path, '/api/v1/results')
        self.assertDictEqual(req.querystring, expected)


class TestFunctestCommand(unittest.TestCase):
    """Tests for FunctestCommand class"""

    def test_backend_class(self):
        """Test if the backend class is Functest"""

        self.assertIs(FunctestCommand.BACKEND, Functest)

    def test_setup_cmd_parser(self):
        """Test if it parser object is correctly initialized"""

        parser = FunctestCommand.setup_cmd_parser()
        self.assertIsInstance(parser, BackendCommandArgumentParser)
        self.assertEqual(parser._backend, Functest)

        args = ['--from-date', '1970-01-01',
                '--to-date', '2010-01-01',
                'http://example.com']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.url, 'http://example.com')
        self.assertEqual(parsed_args.from_date, DEFAULT_DATETIME)
        self.assertEqual(parsed_args.to_date,
                         datetime.datetime(2010, 1, 1, 0, 0, 0,
                                           tzinfo=dateutil.tz.tzutc()))
        self.assertTrue(parsed_args.ssl_verify)

        args = ['http://example.com', '--no-archive', '--no-ssl-verify']
        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.url, 'http://example.com')
        self.assertTrue(parsed_args.no_archive)
        self.assertFalse(parsed_args.ssl_verify)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
