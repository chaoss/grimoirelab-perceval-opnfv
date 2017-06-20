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

import logging

import requests

from grimoirelab.toolkit.datetime import datetime_to_utc
from grimoirelab.toolkit.uris import urijoin


logger = logging.getLogger(__name__)


class FunctestClient:
    """Functest REST API client.

    This class implements a simple client to retrieve data
    from a Functest site using its REST API v1.

    :param base_url: URL of the Functest server
    """
    FUNCTEST_API_PATH = "/api/v1/"

    # API resources
    RRESULTS = 'results'

    # API parameters
    PFROM_DATE = 'from'
    PTO_DATE = 'to'

    def __init__(self, base_url):
        self.base_url = base_url

    def results(self, from_date, to_date):
        """Get test cases results."""

        fdt = from_date.strftime("%Y-%m-%d %H:%M:%S")
        tdt = to_date.strftime("%Y-%m-%d %H:%M:%S")

        params = {
            self.PFROM_DATE: fdt,
            self.PTO_DATE: tdt
        }
        response = self._fetch(self.RRESULTS, params)

        return response

    def _fetch(self, resource, params):
        """Fetch a resource.

        :param resource: resource to fetch
        :param params: dict with the HTTP parameters needed to call
            the given method
        """
        url = urijoin(self.base_url, self.FUNCTEST_API_PATH, resource)

        logger.debug("Functest client requests: %s params: %s",
                     resource, str(params))

        r = requests.get(url, params=params)
        r.raise_for_status()

        return r.text
