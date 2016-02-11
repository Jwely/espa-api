from api.domain import sensor
from api.dbconnect import DBConnect
from api.utils import api_cfg
from validate_email import validate_email
from api.providers.ordering import ProviderInterfaceV0
import yaml
import copy

from api.api_logging import api_logger as logger

class OrderingProvider(ProviderInterfaceV0):

    @staticmethod
    def sensor_products(product_id):
        # coming from uwsgi, product_id is unicode
        if isinstance(product_id, basestring):
            prod_list = product_id.split(",")
        else:
            prod_list = product_id

        return sensor.available_products(prod_list)

    @staticmethod
    def fetch_user(username):
        userlist = []
        with DBConnect(**api_cfg()) as db:
            # username uniqueness enforced on auth_user table at database
            user_sql = "select id, username, email, is_staff, is_active, " \
                       "is_superuser from auth_user where username = %s;"
            db.select(user_sql, (username))

        return db[0]

    @staticmethod
    def staff_products(product_id):
        all_prods = copy.deepcopy(OrderingProvider.sensor_products(product_id))
        return all_prods

    @staticmethod
    def pub_products(product_id):
        pub_prods = copy.deepcopy(OrderingProvider.sensor_products(product_id))
        with open('api/domain/restricted.yaml') as f:
            restricted_list = yaml.load(f.read())
        for prod in restricted_list['internal_only']:
            for sensor_type in pub_prods.keys():
                if prod in pub_prods[sensor_type]['outputs']:
                    pub_prods[sensor_type]['outputs'].remove(prod)

        return pub_prods

    def available_products(self, product_id, username):
        userlist = OrderingProvider.fetch_user(username)
        return_prods = {}
        if userlist['is_staff']:
            return_prods = OrderingProvider.staff_products(product_id)
        else:
            return_prods = OrderingProvider.pub_products(product_id)

        return return_prods

    def fetch_user_orders(self, uid):
        id_type = 'email' if validate_email(uid) else 'username'
        order_list = []
        out_dict = {}
        user_ids = []

        with DBConnect(**api_cfg()) as db:
            user_sql = "select id, username, email from auth_user where "
            user_sql += "email = %s;" if id_type == 'email' else "username = %s;"
            db.select(user_sql, (uid))
            # username uniqueness enforced on the db
            # not the case for emails though
            if db:
                user_ids = [db[ind][0] for ind, val in enumerate(db)]

            if user_ids:
                user_tup = tuple([str(idv) for idv in user_ids])
                sql = "select orderid from ordering_order where user_id in {};".format(user_tup)
                sql = sql.replace(",)",")")
                db.select(sql)
                if db:
                    order_list = [item[0] for item in db]

        out_dict["orders"] = order_list
        return out_dict

    def fetch_order(self, ordernum):
        sql = "select * from ordering_order where orderid = %s;"
        out_dict = {}
        opts_dict = {}
        scrub_keys = ['initial_email_sent', 'completion_email_sent', 'id', 'user_id',
			'ee_order_id', 'email']

        with DBConnect(**api_cfg()) as db:
            db.select(sql, (str(ordernum)))
            if db:
                for key, val in db[0].iteritems():
                    out_dict[key] = val
                opts_str = db[0]['product_options']
                opts_str = opts_str.replace("\n","")
                opts_dict = yaml.load(opts_str)
		out_dict['product_options'] = opts_dict

        for k in scrub_keys:
            if k in out_dict.keys():
                out_dict.pop(k)

        return out_dict

    def place_order(self, username, order):
        pass

    def order_status(self, orderid):
        sql = "select orderid, status from ordering_order where orderid = %s;"
        response = {}
        with DBConnect(**api_cfg()) as db:
            db.select(sql, str(orderid))
            if db:
                for i in ['orderid','status']:
                    response[i] = db[0][i]
            else:
                response['msg'] = 'sorry, no orders matched orderid %s' % orderid

        return response

    def item_status(self, orderid, itemid='ALL'):
        response = {}
        sql = "select oo.orderid, os.name, os.status, os.completion_date, os.note "\
              "from ordering_order oo left join ordering_scene os on oo.id = "\
              "os.order_id where oo.orderid = %s"
        if itemid is not "ALL":
            argtup = (orderid, itemid)
            sql += " AND os.name = %s;"
        else:
            argtup = (str(orderid))
            sql += ";"

        with DBConnect(**api_cfg()) as db:
            db.select(sql, argtup)

        if db:
            for key in ('orderid', 'name', 'status', 'completion_date', 'note'):
                for i in enumerate(db):
                    val = db[i[0]][key]
                    if key is 'completion_date':
                        val = val.strftime("%M-%d-%y %I:%m:%S")
                    response[key] = val
        else:
            response['msg'] = 'sorry, no items matched orderid %s , itemid %s' % (orderid, itemid)

        return response

    def fetch_production_products(self, params):
        cur_params = ('priority','user','sensor')
        invalid_params = []
        for i in params:
            if i not in cur_params:
                invalid_params.append(i)

        if invalid_params:
            return {"msg": "invalid parameters: " + ", ".join(invalid_params)}


        response = {}
        return response

    def get_products_to_process(record_limit=500,
                                for_user=None,
                                priority=None,
                                product_types=['landsat', 'modis'],
                                encode_urls=False):
        '''Find scenes that are oncache and return them as properly formatted
        json per the interface description between the web and processing tier'''

        logger.info('Retrieving products to process...')
        logger.debug('Record limit:{0}'.format(record_limit))
        logger.debug('Priority:{0}'.format(priority))
        logger.debug('For user:{0}'.format(for_user))
        logger.debug('Product types:{0}'.format(product_types))
        logger.debug('Encode urls:{0}'.format(encode_urls))

        buff = StringIO()
        buff.write('WITH order_queue AS ')
        buff.write('(SELECT u.email "email", count(name) "running" ')
        buff.write('FROM ordering_scene s ')
        buff.write('JOIN ordering_order o ON o.id = s.order_id ')
        buff.write('JOIN auth_user u ON u.id = o.user_id ')
        buff.write('WHERE ')
        buff.write('s.status in (\'queued\', \'processing\') ')
        buff.write('GROUP BY u.email) ')
        buff.write('SELECT ')
        buff.write('p.contactid, ')
        buff.write('s.name, ')
        buff.write('s.sensor_type, ')
        buff.write('o.orderid, ')
        buff.write('o.product_options, ')
        buff.write('o.priority, ')
        buff.write('o.order_date, ')
        buff.write('q.running ')
        buff.write('FROM ordering_scene s ')
        buff.write('JOIN ordering_order o ON o.id = s.order_id ')
        buff.write('JOIN auth_user u ON u.id = o.user_id ')
        buff.write('JOIN ordering_userprofile p ON u.id = p.user_id ')
        buff.write('LEFT JOIN order_queue q ON q.email = u.email ')
        buff.write('WHERE ')
        buff.write('o.status = \'ordered\' ')
        buff.write('AND s.status = \'oncache\' ')

        if product_types is not None and len(product_types) > 0:
            type_str = ','.join('\'{0}\''.format(x) for x in product_types)
            buff.write('AND s.sensor_type IN ({0}) '.format(type_str))

        if for_user is not None:
            buff.write('AND u.username = \'{0}\' '.format(for_user))

        if priority is not None:
            buff.write('AND o.priority = \'{0}\' '.format(priority))

        buff.write('ORDER BY q.running ASC NULLS FIRST, ')
        buff.write('o.order_date ASC LIMIT {0}'.format(record_limit))

        query = buff.getvalue()
        buff.close()
        logger.debug("QUERY:{0}".format(query))

        query_results = None
        cursor = connection.cursor()

        if cursor is not None:
            try:
                cursor.execute(query)
                query_results = utilities.dictfetchall(cursor)
            finally:
                if cursor is not None:
                    cursor.close()

        # Need the results reorganized by contact id so we can get dload urls from
        # ee in bulk by id.
        by_cid = {}
        for result in query_results:
            cid = result.pop('contactid')
            # ['orderid', 'sensor_type', 'contactid', 'name', 'product_options']
            by_cid.setdefault(cid, []).append(result)

        #this will be returned to the caller
        results = []
        for cid in by_cid.keys():
            cid_items = by_cid[cid]

            landsat = [item['name'] for item in cid_items if item['sensor_type'] == 'landsat']
            logger.debug('Retrieving {0} landsat download urls for cid:{1}'
                         .format(len(landsat), cid))

            start = datetime.datetime.now()
            landsat_urls = lta.get_download_urls(landsat, cid)
            stop = datetime.datetime.now()
            interval = stop - start
            logger.debug('Retrieving download urls took {0} seconds'
                         .format(interval.seconds))
            logger.debug('Retrieved {0} landsat urls for cid:{1}'.format(len(landsat_urls), cid))

            modis = [item['name'] for item in cid_items if item['sensor_type'] == 'modis']
            modis_urls = lpdaac.get_download_urls(modis)

            logger.debug('Retrieved {0} urls for cid:{1}'.format(len(modis_urls), cid))

            for item in cid_items:
                dload_url = None
                if item['sensor_type'] == 'landsat':

                     # check to see if the product is still available

                    if ('status' in landsat_urls[item['name']] and
                            landsat_urls[item['name']]['status'] != 'available'):
                        try:
                            limit = config.get('retry.retry_missing_l1.retries')
                            timeout = config.get('retry.retry_missing_l1.timeout')
                            ts = datetime.datetime.now()
                            after = ts + datetime.timedelta(seconds=timeout)

                            logger.info('{0} for order {1} was oncache '
                                        'but now unavailable, reordering'
                                        .format(item['name'], item['orderid']))

                            set_product_retry(item['name'],
                                              item['orderid'],
                                              'get_products_to_process',
                                              'product was not available',
                                              'reorder missing level1 product',
                                              after, limit)
                        except Exception:

                            logger.info('Retry limit exceeded for {0} in '
                                        'order {1}... moving to error status.'
                                        .format(item['name'], item['orderid']))

                            set_product_error(item['name'], item['orderid'],
                                              'get_products_to_process',
                                              ('level1 product data '
                                               'not available after EE call '
                                               'marked product as available'))
                        continue

                    if 'download_url' in landsat_urls[item['name']]:
                        logger.info('download_url was in landsat_urls for {0}'.format(item['name']))
                        dload_url = landsat_urls[item['name']]['download_url']
                        if encode_urls:
                            dload_url = urllib.quote(dload_url, '')

                elif item['sensor_type'] == 'modis':
                    if 'download_url' in modis_urls[item['name']]:
                        dload_url = modis_urls[item['name']]['download_url']
                        if encode_urls:
                            dload_url = urllib.quote(dload_url, '')

                result = {
                    'orderid': item['orderid'],
                    'product_type': item['sensor_type'],
                    'scene': item['name'],
                    'priority': item['priority'],
                    'options': json.loads(item['product_options'])
                }

                if item['sensor_type'] == 'plot':
                    # no dload url for plot items, just append it
                    results.append(result)
                elif dload_url is not None:
                    result['download_url'] = dload_url
                    results.append(result)
                else:
                    logger.info('dload_url for {0} in order {0} '
                                'was None, skipping...'
                                .format(item['orderid'], item['name']))
        return results




