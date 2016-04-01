from api.util.dbconnect import DBConnectException, db_instance
from api.providers.reporting import ReportingProviderInterfaceV0
from api.system.logger import ilogger as logger
from api.providers.reporting import REPORTS
from api.providers.reporting import STATS

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

    def stat_list(self, show_query=False):
        # make a copy of this as we dont want to modify the
        # actual dict in this module
        _stats = copy.deepcopy(STATS)

        for key, value in _stats.iteritems():
            if show_query is False:
                value.pop('query')
        return _stats

    def get_stat(self, name, skip_cache=False):

        if name not in STATS:
            raise NotImplementedError

        query = STATS[name]['query']

        if query is not None and len(query) > 0:
            with db_instance() as db:
                db.select(query)
                result = db.dictfetchall
                stat = result[0]['statistic']
            return stat
        else:
            logger.debug("Query was empty for {0}: {1}".format(name, query))
            return None

