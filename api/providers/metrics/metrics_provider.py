import re
import os
import datetime
import urllib2
import gzip
import calendar
from collections import defaultdict

from api.providers.metrics import MetricsProviderInterface
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.util.dbconnect import db_instance
from api.domain.sensor import SensorCONST
from api.util.sshcmd import RemoteHost


class MetricsProviderException(Exception):
    pass


class MetricsProvider(MetricsProviderInterface):
    def __init__(self):
        self.config = ConfigurationProvider()
        self.sensor_keys = SensorCONST.instances.keys()

        self.user = self.config.get('landsatds.username')
        self.pw = self.config.get('landsatds.password')

    def previous_month(self):
        """
        Put together metrics for the previous month then
        email the results out
        """
        recieve = self.config.get('email.stats_notification').split(',')
        sender = self.config.get('email.espa_address').split(',')

        msg = ''
        begin_date, end_date = self.date_range()
        subject = 'LSRD ESPA Metrics for {0} to {1}'.format(begin_date,
                                                            end_date)

        try:
            # Fetch and process the web logs
            infodict, order_paths = self.process_weblogs(begin_date,
                                                         end_date)

            # Downloads by Product
            orders_scenes = self.extract_orderid(order_paths)

            if not orders_scenes:
                raise ValueError

            prod_opts = self.db_dl_prodinfo(cfg, orders_scenes)
            infodict = self.tally_product_dls(orders_scenes, prod_opts)
            msg += self.prod_boiler(infodict)

            # On-Demand users and orders placed information
            for source in self.ORDER_SOURCES:
                infodict = self.db_orderstats(source, rng[0], rng[1], cfg)
                infodict.update(self.db_scenestats(source, rng[0], rng[1], cfg))
                infodict['tot_unique'] = self.db_uniquestats(source, rng[0], rng[1], cfg)
                infodict['who'] = source.upper()
                msg += self.ondemand_boiler(infodict)

            # Orders by Product
            infodict = self.db_prodinfo(cfg, rng[0], rng[1])
            msg += self.prod_boiler(infodict)

        except Exception:
            exc_msg = str(traceback.format_exc()) + '\n\n' + msg
            utils.send_email(sender, debug, subject, exc_msg)
            msg = ('There was an error with statistics processing.\n'
                   'The following have been notified of the error: {0}.'
                   .format(', '.join(debug)))
            raise
        finally:
            utils.send_email(sender, receive, subject, msg)

            if os.path.exists(LOCAL_LOG):
                os.remove(LOCAL_LOG)

    def process_weblogs(self, begin_date, end_date):
        """
        Retrieve the weblogs from the remote servers, then process them
        to determine what and how much was downloaded

        :return:
        """
        infodict = {'tot_dl': 0,
                    'tot_vol': 0.0}
        order_paths = []

        logs = self.config.url_for('weblogs').split(',')
        local_path = self.config.url_for('tmp')
        for log in logs:
            host, remote_path = log.split(':')
            remote_log = remote_path.format(datetime.datetime
                                            .today()
                                            .replace(day=1)
                                            .strftime('%Y%m01'))

            local_log = os.path.join(local_path,
                                     os.path.split(remote_log)[-1])

            with RemoteHost(host=host, user=self.user, pw=self.pw) as r:
                r.get(remote_log, local_log)

            info, order_p = self.calc_dlinfo(local_log,
                                                     begin_date,
                                                     end_date)

            for k in infodict:
                infodict[k] += info[k]

            order_paths.extend(order_p)

            os.remove(local_log)

        return infodict, order_paths


    @staticmethod
    def download_boiler(info):
        """
        Boiler plate text for On-Demand Info for downloads

        :param info: values to insert into the boiler plate
        :param info: dict
        :return: formatted string
        """
        boiler = ('\n==========================================\n'
                  ' On-demand - Download Info\n'
                  '==========================================\n'
                  'Total number of ordered scenes downloaded through ESPA order interface order links: {tot_dl}\n'
                  'Total volume of ordered scenes downloaded (GB): {tot_vol}\n')

        return boiler.format(**info)

    @staticmethod
    def ondemand_boiler(info):
        """
        Boiler plate text for On-Demand Info for orders

        :param info: values to insert into the boiler plate
        :param info: dict
        :return: formatted string
        """
        boiler = ('\n==========================================\n'
                  ' On-demand - {who}\n'
                  '==========================================\n'
                  ' Total scenes ordered in the month for {who} interface: {scenes_month}\n'
                  ' Number of scenes ordered in the month (USGS) for {who} interface: {scenes_usgs}\n'
                  ' Number of scenes ordered in the month (non-USGS) for {who} interface: {scenes_non}\n'
                  ' Total orders placed in the month for {who} interface: {orders_month}\n'
                  ' Number of total orders placed in the month (USGS) for {who} interface: {orders_usgs}\n'
                  ' Number of total orders placed in the month (non-USGS) for {who} interface: {orders_non}\n'
                  ' Total number of unique On-Demand users for {who} interface: {tot_unique}\n')

        return boiler.format(**info)

    @staticmethod
    def prod_boiler(info):
        """
        Boiler plate text for On-Demand Info for products breakdown

        :param info: values to insert into the boiler plate
        :param info: dict
        :return: formatted string
        """
        boiler = ('\n==========================================\n'
                  ' {title}\n'
                  '==========================================\n'
                  ' Total Scenes: {total}\n'
                  ' SR: {sr}\n'
                  ' SR Thermal: {bt}\n'
                  ' ToA: {toa}\n'
                  ' Source: {l1}\n'
                  ' Source Metadata: {source_metadata}\n'
                  ' Customized Source: {customized_source_data}\n'
                  ' SR EVI: {sr_evi}\n'
                  ' SR MSAVI: {sr_msavi}\n'
                  ' SR NBR: {sr_nbr}\n'
                  ' SR NBR2: {sr_nbr2}\n'
                  ' SR NDMI: {sr_ndmi}\n'
                  ' SR NDVI: {sr_ndvi}\n'
                  ' SR SAVI: {sr_savi}\n'
                  ' CFMASK: {cloud}\n'
                  ' Plot: {plot}\n')

        return boiler.format(title=info.get('title'),
                             total=info.get('total', 0),
                             sr=info.get('sr', 0),
                             bt=info.get('bt', 0),
                             toa=info.get('toa', 0),
                             customized_source_data=info.get('customized_source_data', 0),
                             source_metadata=info.get('source_metadata', 0),
                             l1=info.get('l1', 0),
                             sr_evi=info.get('sr_evi', 0),
                             sr_msavi=info.get('sr_msavi', 0),
                             sr_nbr=info.get('sr_nbr', 0),
                             sr_nbr2=info.get('sr_nbr2', 0),
                             sr_ndmi=info.get('sr_ndmi', 0),
                             sr_ndvi=info.get('sr_ndvi', 0),
                             sr_savi=info.get('sr_savi', 0),
                             cloud=info.get('cloud', 0),
                             plot=info.get('plot_statistics', 0))

    def db_prodinfo(self, dbinfo, begin_date, end_date):
        """
        Queries the database to build the ordered product counts
        dates are given as ISO 8601 'YYYY-MM-DD'

        :param dbinfo: Database connection information
        :type dbinfo: dict
        :param begin_date: Date to start the counts on
        :type begin_date: str
        :param end_date: Date to end the counts on
        :type end_date: str
        :return: Dictionary of count values
        """
        sql = ('SELECT product_opts, id '
               'FROM ordering_order '
               'WHERE order_date::date >= %s '
               'AND order_date::date <= %s')

        init = defaultdict(int)

        with db_instance() as db:
            db.select(sql, (begin_date, end_date))
            results = reduce(self.counts_prodopts,
                             map(self.process_db_prodopts, [(_[0], _[1], dbinfo) for _ in db]),
                             init)
        results['title'] = 'What was Ordered'
        return results

    def process_db_prodopts(self, args):
        opts = args[0]
        order_id = args[1]
        dbinfo = args[2]
        ret = defaultdict(int)

        with db_instance() as db:
            db.select('select count(*) '
                      'from ordering_scene '
                      'where order_id = {} '
                      'and name != \'plot\''
                      .format(order_id))
            count = int(db[0][0])

        for key in opts:
            if key in self.sensor_keys:
                num = len(opts[key]['inputs'])
                ret['total'] += num

                if 'plot_statistics' in opts and opts['plot_statistics']:
                    ret['plot_statistics'] += num

                for prod in opts[key]['products']:
                    if prod == 'l1' and ('projection' in opts or
                                         'image_extents' in opts):
                        ret['customized_source_data'] += num
                    else:
                        ret[prod] += num
        if ret['total'] != count:
            NOT_COUNTED.append((order_id, count, ret['total']))
        return ret

    @staticmethod
    def counts_prodopts(*dicts):
        ret = defaultdict(int)
        for d in dicts:
            for k, v in d.items():
                ret[k] += v
        return dict(ret)

    def db_dl_prodinfo(self, dbinfo, orders_scenes):
        """
        Queries the database to get the associated product options

        This query is meant to go with downloads by product

        :param dbinfo: Database connection information
        :type dbinfo: dict
        :param orders_scenes: Order id's that have been downloaded from
         based on web logs and scene names
        :type orders_scenes: tuple
        :return: Dictionary of count values
        """
        ids = zip(*orders_scenes)[0]
        ids = self.remove_duplicates(ids)

        sql = ('SELECT o.orderid, o.product_opts '
               'FROM ordering_order o '
               'WHERE o.orderid = ANY (%s)')

        with db_instance() as db:
            db.select(sql, (ids, ))
            results = {k: val for k, val in db.fetcharr}

        return results

    @staticmethod
    def remove_duplicates(arr_obj):
        return list(set(arr_obj))

    def tally_product_dls(self, orders_scenes, prod_options):
        """
        Counts the number of times a product has been downloaded

        :param orders_scenes: Order id's and scenes that have been
         downloaded from based on web logs, paired tuple
        :type orders_scenes: tuple
        :param prod_options: Unique order id's and their associated product
            options, dict keyed on order id
        :type prod_options: list
        :return: dictionary count
        """
        results = defaultdict(int)

        for orderid, scene in orders_scenes:
            opts = prod_options[urllib2.unquote(orderid)]

            if 'plot_statistics' in opts and opts['plot_statistics']:
                results['plot_statistics'] += 1

            for key in self.sensor_keys:
                if key in opts:
                    # Scene names get truncated during distribution
                    if [x for x in opts[key]['inputs'] if scene in x]:
                        results['total'] += 1

                        for prod in opts[key]['products']:
                            if prod == 'l1' and ('projection' in opts or
                                                 'image_extents' in opts):
                                results['customized_source_data'] += 1
                            else:
                                results[prod] += 1

        results['title'] = 'Downloads by Product'
        return results

    def calc_dlinfo(self, log_file, start_date, end_date):
        """
        Count the total tarballs downloaded from /orders/ and their combined size

        :param log_file: Combined Log Format file path
        :type log_file: str
        :return: Dictionary of values
        """
        infodict = {'tot_dl': 0,
                    'tot_vol': 0.0}

        orders = []

        sd = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        ed = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        with gzip.open(log_file) as log:
            for line in log:
                gr = self.filter_log_line(line, sd, ed)
                if gr:
                    infodict['tot_vol'] += int(gr[8])
                    infodict['tot_dl'] += 1
                    orders.append(gr[5])

        # Bytes to GB
        infodict['tot_vol'] /= 1073741824.0

        return infodict, orders

    @staticmethod
    def filter_log_line(line, start_date, end_date):
        """
        Used to determine if a line in the log should be used for metrics
        counting

        Filters to make sure the line follows a regex
        HTTP response is a 200
        HTTP method is a GET
        location is from /orders/
        falls within the date range

        :param line: incoming line from the log
        :param start_date: inclusive start date
        :param end_date: inclusive end date
        :return: regex groups returned from re.match
        """
        # (ip, logname, user, datetime, method, resource, status, size, referrer, agent)
        regex = r'(.*?) (.*?) (.*?) \[(.*?)\] "(.*?) (.*?) (.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'

        try:
            gr = re.match(regex, line).groups()
            ts, tz = gr[3].split()
            dt = datetime.datetime.strptime(ts, r'%d/%b/%Y:%H:%M:%S').date()

            if (gr[7] == '200' and
                    gr[4] == 'GET' and
                    '.tar.gz' in gr[5] and
                    '/orders/' in gr[5] and
                    start_date <= dt <= end_date):

                return gr
        except:
            return False

    @staticmethod
    def db_scenestats(source, begin_date, end_date, dbinfo):
        """
        Queries the database for the number of scenes ordered
        separated by USGS and non-USGS emails
        dates are given as ISO 8601 'YYYY-MM-DD'

        :param source: EE or ESPA
        :type source: str
        :param begin_date: Date to start the count on
        :type begin_date: str
        :param end_date: Date to stop the count on
        :type end_date: str
        :param dbinfo: Database connection information
        :type dbinfo: dict
        :return: Dictionary of the counts
        """
        sql = ('''select COUNT(*)
                  from ordering_scene
                  inner join ordering_order on ordering_scene.order_id = ordering_order.id
                  where ordering_order.order_date::date >= %s
                  and ordering_order.order_date::date <= %s
                  and ordering_order.orderid like '%%@usgs.gov-%%'
                  and ordering_order.order_source = %s
                  and name != 'plot' ''',
               '''select COUNT(*)
                  from ordering_scene
                  inner join ordering_order on ordering_scene.order_id = ordering_order.id
                  where ordering_order.order_date::date >= %s
                  and ordering_order.order_date::date <= %s
                  and ordering_order.orderid not like '%%@usgs.gov-%%'
                  and ordering_order.order_source = %s
                  and name != 'plot' ''')

        counts = {'scenes_month': 0,
                  'scenes_usgs': 0,
                  'scenes_non': 0}

        with db_instance() as db:
            for q in sql:
                db.select(q, (begin_date, end_date, source))

                if 'not like' in q:
                    counts['scenes_non'] += int(db[0][0])
                else:
                    counts['scenes_usgs'] += int(db[0][0])

        counts['scenes_month'] = counts['scenes_usgs'] + counts['scenes_non']

        return counts

    @staticmethod
    def db_orderstats(source, begin_date, end_date, dbinfo):
        """
        Queries the database to get the total number of orders
        separated by USGS and non-USGS emails
        dates are given as ISO 8601 'YYYY-MM-DD'

        :param source: EE or ESPA
        :type source: str
        :param begin_date: Date to start the count on
        :type begin_date: str
        :param end_date: Date to stop the count on
        :type end_date: str
        :param dbinfo: Database connection information
        :type dbinfo: dict
        :return: Dictionary of the counts
        """
        sql = ('''select COUNT(*)
                  from ordering_order
                  where order_date::date >= %s
                  and order_date::date <= %s
                  and orderid like '%%@usgs.gov-%%'
                  and order_source = %s;''',
               '''select COUNT(*)
                  from ordering_order
                  where order_date::date >= %s
                  and order_date::date <= %s
                  and orderid not like '%%@usgs.gov-%%'
                  and order_source = %s;''')

        counts = {'orders_month': 0,
                  'orders_usgs': 0,
                  'orders_non': 0}

        with db_instance() as db:
            for q in sql:
                db.select(q, (begin_date, end_date, source))

                if 'not like' in q:
                    counts['orders_non'] += int(db[0][0])
                else:
                    counts['orders_usgs'] += int(db[0][0])

        counts['orders_month'] = counts['orders_usgs'] + counts['orders_non']

        return counts

    @staticmethod
    def db_uniquestats(source, begin_date, end_date, dbinfo):
        """
        Queries the database to get the total number of unique users
        dates are given as ISO 8601 'YYYY-MM-DD'

        :param source: EE or ESPA
        :type source: str
        :param begin_date: Date to start the count on
        :type begin_date: str
        :param end_date: Date to stop the count on
        :type end_date: str
        :param dbinfo: Database connection information
        :type dbinfo: dict
        :return: Dictionary of the count
        """
        sql = '''select count(distinct(split_part(orderid, '-', 1)))
                 from ordering_order
                 where order_date::date >= %s
                 and order_date::date <= %s
                 and order_source = %s;'''

        with db_instance() as db:
            db.select(sql, (begin_date, end_date, source))
            return db[0][0]

    @staticmethod
    def date_range():
        """
        Builds two strings for the 1st and last day of
        the previous month, ISO 8601 'YYYY-MM-DD'

        :return: 1st day, last day
        """
        first = datetime.datetime.today().replace(day=1)
        last = first - datetime.timedelta(days=2)

        num_days = calendar.monthrange(last.year, last.month)[1]

        begin_date = '{0}-{1}-1'.format(last.year, last.month)
        end_date = '{0}-{1}-{2}'.format(last.year, last.month, num_days)

        return begin_date, end_date

    @staticmethod
    def extract_orderid(order_paths):
        '/orders/earthengine-landsat@google.com-11022015-210201/LT50310341990240-SC20151130234238.tar.gz'
        return tuple((x[2], x[3].split('-')[0])
                     for x in
                     [i.split('/') for i in order_paths])

