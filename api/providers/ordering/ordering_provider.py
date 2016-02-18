from api.domain import sensor
from api.domain.scene import Scene
from api.domain.config import ApiConfig
from api.dbconnect import DBConnect, DBConnectException
from api.utils import api_cfg
from validate_email import validate_email
from api.providers.ordering import ProviderInterfaceV0
from api import errors
from api import lpdaac

import yaml
import copy

from cStringIO import StringIO

from api.api_logging import api_logger as logger

config = ApiConfig()

class OrderingProviderException(Exception):
    pass

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

    def set_product_retry(self, name, orderid, processing_loc,
                        error, note, retry_after, retry_limit=None):
        """ Set a product to retry status """
        order_id = Scene.get('order_id', name=name, orderid=orderid)
        retry_count = Scene.get('retry_count', name=name, orderid=orderid)
        curr_limit = Scene.get('retry_limit', name=name, orderid=orderid)

        sql_list = ["update ordering_scene set "]
        comm_sep = ""
        if retry_limit is not None:
            comm_sep = ", "
            sql_list.append("retry_limit = {0}".format(retry_limit))
            curr_limit = retry_limit

        if retry_count + 1 <= curr_limit:
            sql_list.append(comm_sep)
            sql_list.append(" status = 'retry', ")
            sql_list.append(" retry_count = {0}, ".format(retry_count + 1))
            sql_list.append(" retry_after = {0}, ".format(retry_after))
            sql_list.append(" log_file_contents = '{0}', ".format(error))
            sql_list.append(" processing_loc = '{0}', ".format(processing_loc))
            sql_list.append(" note = '{0}'".format(note))
        else:
            raise OrderingProviderException("Exception Retry limit exceeded, name: {0}".format(name))

        sql_list.append(" where name = '{0}' AND order_id = {1};".format(name, order_id)
        sql = " ".join(sql_list)
        try:
            with DBConnect(**api_cfg()) as db:
                db.execute(sql)
                db.commit()
        except DBConnectException, e:
            message = "DBConnectException set_product_retry. message: {0}\nsql: {1}".format(e.message, sql)
            raise OrderingProviderException(message)

        return True

    def set_product_error(self, name=None, orderid=None,
                            processing_loc=None, error=None):

        sql_list = ["update ordering_scene set "]
        resolution = errors.resolve(error, name)
        order_id = Scene.get('order_id', name=name, orderid=orderid)

        if resolution is not None:
            if resolution.status == 'submitted':
                sql_list.append(" status = 'submitted', note = '' ")
            elif resolution.status == 'unavailable':
                now = datetime.datetime.now()
                sql_list.append(" status = 'unavailable', processing_location = '{0}', "\
                                "completion_date = {1}, log_file_contents = '{2}', "\
                                "note = '{3}' ".format(processing_loc, now, error, resolution.reason))

                ee_order_id = Scene.get('ee_order_id', name=name, orderid=orderid)
                ee_unit_id = Scene.get('ee_unit_id', name=name, orderid=orderid)
                lta.update_order_status(ee_order_id, ee_unit_id, 'R')

            elif resolution.status == 'retry':
                try:
                    set_product_retry(name, orderid, processing_loc, error,
                                        resolution.reason,
                                        resolution.extra['retry_after'],
                                        resolution.extra['retry_limit'])
                except Exception, e:
                    logger.debug("Exception setting {0} to retry:{1}".format(name, e))
                    sql_list.append(" status = 'error', processing_location = '{0}',"\
                                    " log_file_contents = {1} ".format(processing_loc, error))
        else:
            status = 'error'
            sql_list.append(" status = '{0}', processing_location = '{1}',"\
                            " log_file_contents = '{2}' ".format(status, processing_loc, error))

        sql_list.append(" where name = '{0}' AND order_id = {1};".format(name, order_id))
        sql = " ".join(sql_list)

        try:
            with DBConnect(**api_cfg()) as db:
                db.execute(sql)
                db.commit()
        except DBConnectException, e:
            message = "DBConnectException set_product_error. message: {0}\nsql: {1}".format(e.message, sql)
            raise OrderingProviderException(message)

        return True

    def get_products_to_process(self, record_limit=500,
                                for_user=None,
                                priority=None,
                                product_types=['landsat', 'modis'],
                                encode_urls=False):
        '''Find scenes that are oncache and return them as properly formatted
        json per the interface description between the web and processing tier'''

        logger.info('Retrieving products to process...')
        logger.warn('Record limit:{0}'.format(record_limit))
        logger.warn('Priority:{0}'.format(priority))
        logger.warn('For user:{0}'.format(for_user))
        logger.warn('Product types:{0}'.format(product_types))
        logger.warn('Encode urls:{0}'.format(encode_urls))

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
        logger.warn("QUERY:{0}".format(query))

        query_results = None

        with DBConnect(**api_cfg()) as db:
            db.select(query)

        query_results = db.fetcharr

        # Need the results reorganized by contact id so we can get dload urls from
        # ee in bulk by id.
        by_cid = {}
        for result in query_results:
            cid = result['contactid']
            # ['orderid', 'sensor_type', 'contactid', 'name', 'product_options']
            by_cid.setdefault(cid, []).append(result)

        #this will be returned to the caller
        results = []
        for cid in by_cid.keys():
            cid_items = by_cid[cid]

            landsat = [item['name'] for item in cid_items if item['sensor_type'] == 'landsat']
            logger.warn('Retrieving {0} landsat download urls for cid:{1}'
                         .format(len(landsat), cid))

            start = datetime.datetime.now()
            landsat_urls = lta.get_download_urls(landsat, cid)
            stop = datetime.datetime.now()
            interval = stop - start
            logger.warn('Retrieving download urls took {0} seconds'
                         .format(interval.seconds))
            logger.warn('Retrieved {0} landsat urls for cid:{1}'.format(len(landsat_urls), cid))

            modis = [item['name'] for item in cid_items if item['sensor_type'] == 'modis']
            modis_urls = lpdaac.get_download_urls(modis)

            logger.warn('Retrieved {0} urls for cid:{1}'.format(len(modis_urls), cid))

            for item in cid_items:
                dload_url = None
                if item['sensor_type'] == 'landsat':

                     # check to see if the product is still available

                    if ('status' in landsat_urls[item['name']] and
                            landsat_urls[item['name']]['status'] != 'available'):
                        try:
                            limit = config.settings['retry.retry_missing_l1.retries']
                            timeout = config.settings['retry.retry_missing_l1.timeout']
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

    def update_status(self, name=None, orderid=None,
                        processing_loc=None, status=None):
        order_id = Scene.get('order_id', name=name, orderid=orderid)
        sql_list = ["update ordering_scene set "]
        comm_sep = ""
        if processing_loc:
            sql_list.append(" processing_location = '%s' " % processing_loc)
            comm_sep = ", "
        if status:
            sql_list.append(comm_sep)
            sql_list.append(" status = '%s'" % status)

        sql_list.append(" where name = '{0}' AND order_id = {1};".format(name, order_id))
        sql = " ".join(sql_list)

        try:
            with DBConnect(**api_cfg()) as db:
                db.execute(sql)
                db.commit()
        except DBConnectException, e:
            message = "DBConnect Exception ordering_provider update_status sql: {0}\nmessage: {1}".format(sql, e.message)
            raise OrderingProviderException(message)

        return True

    def set_product_unavailable(self, name=None, orderid=None,
                                processing_loc=None, error=None, note=None):

        order_id = Scene.get('order_id', name=name, orderid=orderid)
        order_source = Scene.get('order_source', name=name, orderid=orderid)
        sql_list = ["update ordering_scene set "]
        sql_list.append(" status = 'unavailable', ")
        sql_list.append(" processing_location = '{0}', ".format(processing_loc))
        sql_list.append(" completion_date = {0}, ".format(datetime.datetime.now()))
        sql_list.append(" log_file_contents = '{0}', ".format(error))
        sql_list.append(" note = '{0}' ".format(note))
        sql_list.append(" where name = '{0}' AND order_id = {1};".format(name, order_id))
        sql = " ".join(sql_list)

        if order_source == 'ee':
            # update EE
            ee_order_id = Scene.get('ee_order_id', name=name, orderid=orderid)
            ee_unit_id = Scene.get('ee_unit_id', name=name, orderid=orderid)
            lta.update_order_status(ee_order_id, ee_unit_id, 'R')

        try:
            with DBConnect(**api_cfg()) as db:
                db.execute(sql)
                db.commit()
        except DBConnectException, e:
            message = "DBConnect Exception ordering_provider set_product_unavailable sql: {0}\nmessage: {1}".format(sql, e.message)
            raise OrderingProviderException(message)

        return True

    def mark_product_complete(self, name=None, orderid=None, processing_loc=None,
                                completed_file_location=None, destination_cksum_file=None,
                                log_file_contents=None):

        order_id = Scene.get('order_id', name=name, orderid=orderid)
        order_source = Scene.get('order_source', name=name, orderid=orderid)
        base_url = config.url_for('distribution.cache')

        product_file_parts = completed_file_location.split('/')
        product_file = product_file_parts[len(product_file_parts) - 1]
        cksum_file_parts = destination_cksum_file.split('/')
        cksum_file = cksum_file_parts[len(cksum_file_parts) - 1]

        product_dload_url = ('%s/orders/%s/%s') % (base_url, orderid, product_file)
        cksum_download_url = ('%s/orders/%s/%s') % (base_url, orderid, cksum_file)

        sql_list = ["update ordering_scene set "]
        sql_list.append(" status = 'complete', ")
        sql_list.append(" processing_location = '{0}', ".format(processing_loc))
        sql_list.append(" product_distro_location = '{0}', ".format(completed_file_location))
        sql_list.append(" completion_date = {0}, ".format(datetime.datetime.now()))
        sql_list.append(" cksum_distro_location = '{0}', ".format(destination_cksum_file))
        sql_list.append(" log_file_contents = '{0}', ".format(log_file_contents))
        sql_list.append(" product_dload_url = '{0}', ".format(product_dload_url))
        sql_list.append(" cksum_download_url = '{0}' ".format(cksum_download_url))
        sql_list.append(" where name = '{0}' AND order_id = {1};".format(name, order_id))
        sql = " ".join(sql_list)

        if order_source == 'ee':
            # update EE
            ee_order_id = Scene.get('ee_order_id', name=name, orderid=orderid)
            ee_unit_id = Scene.get('ee_unit_id', name=name, orderid=orderid)
            lta.update_order_status(ee_order_id, ee_unit_id, 'C')

        try:
            with DBConnect(**api_cfg()) as db:
                db.execute(sql)
                db.commit()
        except DBConnectException, e:
            message = "DBConnect Exception ordering_provider set_product_unavailable sql: {0}\nmessage: {1}".format(sql, e.message)
            raise OrderingProviderException(message)

        return True

    def update_product(self, action, name=None, orderid=None, processing_loc=None,
                        status=None, error=None, note=None,
                        completed_file_location=None,
                        cksum_file_location=None,
                        log_file_contents=None):

        permitted_actions = ('update_status', 'set_product_error',
                            'set_product_unavailable', 'mark_product_complete')

        if action not in permitted_actions:
            return {"msg": "{0} is not an accepted action for update_product".format(action)}

        if action == 'update_status':
            result = self.update_status(name=name, orderid=orderid,
                                        processing_loc=processing_loc, status=status)

        if action == 'set_product_error':
            result = self.set_product_error(name=name, orderid=orderid,
                                            processing_loc=processing_loc, error=error)

        if action == 'set_product_unavailable':
            result = self.set_product_unavailable(name=name, orderid=orderid,
                                                    processing_loc=processing_loc,
                                                    error=error, note=note)

        if action == 'mark_product_complete':
            result = self.mark_product_complete(name=name, orderid=orderid,
                                                processing_loc=processing_loc,
                                                completed_file_location=completed_file_location,
                                                destination_cksum_file=destination_cksum_file,
                                                log_file_contents=log_file_contents)

        return result



# ?? core.handle_orders
# ??  queue_products          (order_name_tuple_list, processing_loc, job_name)





