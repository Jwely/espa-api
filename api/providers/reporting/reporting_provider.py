from api.util.dbconnect import DBConnectException, db_instance
from api.providers.reporting import ReportingProviderInterfaceV0
from api.system.logger import ilogger as logger
from api.providers.reporting import REPORTS
from api.providers.reporting import STATS
from api.providers.configuration.configuration_provider import ConfigurationProvider

import copy
import datetime
import json

config = ConfigurationProvider()


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

    def stat_query(self, name):
        if name not in STATS:
            raise NotImplementedError("value: {0}".format(name))

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

    def get_stat(self, name):
        if name == 'all':
            stat = {}
            for key in STATS.keys():
                val = self.stat_query(key)
                stat[key] = val
        else:
            stat = self.stat_query(name)

        return stat

    def missing_auxiliary_data(self, sensor_group, year=None):
        _sensor_groups = {'L17': {1978: ['ncep', 'toms']},
                          'L8': {2013: ['lads']}}
        _cur_year = datetime.datetime.now().year
        return_dict = {}

        if sensor_group not in _sensor_groups:
            return {"msg": "sensor_group must be either %s" % " or ".join(_sensor_groups.keys())}

        _syear = _sensor_groups[sensor_group].keys()[0]
        if year and int(year) not in range(_syear, _cur_year + 1):
            return {"msg": "auxiliary data is only available from %s to %s" %
                           (_syear, _cur_year)}

        for k, v in _sensor_groups[sensor_group].items():
            for report in v:
                try:
                    rpt_name = ''.join([config.get("aux_report_path"), report, '_report.txt'])
                    report_con = open(rpt_name).read()
                    report_dict = json.loads(report_con.replace("'", "\""))
                    out_d = {}
                    for yr in report_dict:
                        if report_dict[yr] != 0:
                            if not year:
                                out_d[yr] = report_dict[yr]
                            else:
                                if yr == year:
                                    out_d[yr] = report_dict[yr]
                    return_dict[report] = out_d
                except IOError:
                    return {"msg": "%s report could not be found" % report}

        return return_dict
