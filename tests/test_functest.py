# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2017 Bitergia
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
#

import datetime
import sys
import unittest

import httpretty
import pkg_resources

# Hack to make sure that tests import the right packages
# due to setuptools behaviour
sys.path.insert(0, '..')
pkg_resources.declare_namespace('perceval.backends')

from perceval.backends.opnfv.functest import FunctestClient


def read_file(filename, mode='r'):
    with open(filename, mode) as f:
        content = f.read()
    return content


FUNCTEST_URL = "http://example.com/"
FUNCTEST_API_URL = FUNCTEST_URL + 'api/v1/'
FUNCTEST_RESULTS_URL = FUNCTEST_API_URL + 'results'


def setup_http_server():
    """Setup a mock HTTP server"""

    body = read_file('data/functest/functest_results.json', 'rb')

    httpretty.register_uri(httpretty.GET,
                           FUNCTEST_RESULTS_URL,
                           body=body, status=200)


class TestFunctestClient(unittest.TestCase):
    """Functest API client tests.

    These tests do not check the body of the response, only if the call
    was well formed and if a response was obtained. Due to this, take
    into account that the body returned on each request might not
    match with the parameters from the request.
    """
    @httpretty.activate
    def test_repository(self):
        """Test repository API call"""

        # Set up a mock HTTP server
        setup_http_server()

        # Call API
        client = FunctestClient(FUNCTEST_URL)
        from_date = datetime.datetime(2017, 6, 1, 10, 0, 0)
        to_date = datetime.datetime(2017, 6, 1, 11, 0, 0)
        response = client.results(from_date=from_date, to_date=to_date)

        req = httpretty.last_request()

        expected = {
            'from': ['2017-06-01 10:00:00'],
            'to': ['2017-06-01 11:00:00']
        }
        self.assertEqual(req.method, 'GET')
        self.assertRegex(req.path, '/api/v1/results')
        self.assertDictEqual(req.querystring, expected)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
