from api.util.dbconnect import DBConnectException, db_instance
from api.providers.reporting import ReportingProviderInterfaceV0
from api.system.logger import ilogger as logger
from api.providers.reporting import REPORTS

import copy

class ReportingProviderException(Exception):
    pass

class ReportingProvider(ReportingProviderInterfaceV0):

    def listing(self, show_query=False):

        result = {}

        # make a copy of this as we dont want to modify the
        # actual dict in this module
        _reports = copy.deepcopy(REPORTS)

        for key, value in _reports.iteritems():
            if show_query is False:
                value['query'] = ''
            result[key] = value
        return result

    def run(self, name):

        if name not in REPORTS:
            raise NotImplementedError

        query = REPORTS[name]['query']

        if query is not None and len(query) > 0:
            with db_instance() as db:
                db.select(query)
                return db.dictfetchall
        else:
            logger.warn("Query was empty for {0}: {1}".format(name, query))
            return {}


listing = ReportingProvider().listing

run = lambda name: ReportingProvider().run(name)

display_name = lambda name: REPORTS[name]['display_name']



