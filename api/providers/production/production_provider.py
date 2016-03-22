from api.domain import sensor
from api.domain.scene import Scene
from api.domain.order import Order
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.util.dbconnect import DBConnectException, db_instance
from api.providers.production import ProductionProviderInterfaceV0
from api.external import lpdaac, lta, onlinecache, nlaps
from api.system import errors
from api.notification import emails
from api.domain.user import User
from api.providers.ordering.options_conversion import convert_options

import copy
import memcache
import datetime
import urllib

from cStringIO import StringIO

from api.system.logger import api_logger as logger

config = ConfigurationProvider()
cache = memcache.Client(['127.0.0.1:11211'], debug=0)

class ProductionProviderException(Exception):
    pass

class ProductionProvider(ProductionProviderInterfaceV0):

    def queue_products(self, order_name_tuple_list, processing_location, job_name):
        ''' Allows the caller to place products into queued status in bulk '''

        if not isinstance(order_name_tuple_list, list):
            msg = list()
            msg.append("queue_products expects a list of ")
            msg.append("tuples(orderid, scene_name) for the first argument")
            raise TypeError(''.join(msg))

        # this should be a dictionary of lists, with order as the key and
        # the scenes added to the list
        orders = {}

        for order, product_name in order_name_tuple_list:
            if not order in orders:
                orders[order] = list()
            orders[order].append(product_name)

        # now use the orders dict we built to update the db
        for order in orders:
            products = orders[order]

            product_tup = tuple(products)
            order = Order.where("orderid = '{0}'".format(order))[0]
            scene_filters = ["name in {0}".format(product_tup)]
            scene_filters.append("order_id = {0}".format(order.id))
            scenes = Scene.where(scene_filters)

            updates = {"status": "queued",
                        "processing_location": processing_location,
                        "log_file_contents": "''",
                        "note": "''",
                        "job_name": job_name}

            Scene.bulk_update([s.id for s in scenes], updates)

        return True

    def mark_product_complete(self, name, orderid, processing_loc=None,
                                completed_file_location=None, destination_cksum_file=None,
                                log_file_contents=None):

        order_id = Scene.get('order_id', name, orderid)
        order_source = Scene.get('order_source', name, orderid)
        base_url = config.url_for('distribution.cache')

        product_file_parts = completed_file_location.split('/')
        product_file = product_file_parts[len(product_file_parts) - 1]
        cksum_file_parts = destination_cksum_file.split('/')
        cksum_file = cksum_file_parts[len(cksum_file_parts) - 1]

        product_dload_url = ('%s/orders/%s/%s') % (base_url, orderid, product_file)
        cksum_download_url = ('%s/orders/%s/%s') % (base_url, orderid, cksum_file)

        scene = Scene.where("name = '{0}' AND order_id = {1}".format(name, order_id))[0]
        scene.status = 'complete'
        scene.processing_location = processing_loc
        scene.product_distro_location = completed_file_location
        scene.completion_date = datetime.datetime.now()
        scene.cksum_distro_location = destination_cksum_file
        scene.log_file_contents = log_file_contents
        scene.product_dload_url = product_dload_url
        scene.cksum_download_url = cksum_download_url

        if order_source == 'ee':
            # update EE
            ee_order_id = Scene.get('ee_order_id', name, orderid)
            ee_unit_id = Scene.get('ee_unit_id', name, orderid)
            lta.update_order_status(ee_order_id, ee_unit_id, 'C')

        try:
            scene.save()
        except DBConnectException, e:
            message = "DBConnect Exception ordering_provider mark_product_complete sql: {0}"\
                        "\nmessage: {1}".format(sql, e.message)
            raise OrderingProviderException(message)

        return True

    def set_product_unavailable(self, name, orderid,
                                processing_loc=None, error=None, note=None):

        order_id = Scene.get('order_id', name, orderid)
        order_source = Scene.get('order_source', name, orderid)

        scene = Scene.where("name = '{0}' and order_id = {1}".format(name, order_id))[0]
        scene.status = 'unavailable'
        scene.processing_location = processing_loc
        scene.completion_date = datetime.datetime.now()
        scene.log_file_contents = error
        scene.note = note
        scene.save()

        if order_source == 'ee':
            # update EE
            ee_order_id = Scene.get('ee_order_id', name, orderid)
            ee_unit_id = Scene.get('ee_unit_id', name, orderid)
            lta.update_order_status(ee_order_id, ee_unit_id, 'R')

        try:
            scene.save()
        except DBConnectException, e:
            message = "DBConnect Exception ordering_provider set_product_unavailable sql: {0}\nmessage: {1}".format(sql, e.message)
            raise ProductionProviderException(message)

        return True

    @staticmethod
    def set_products_unavailable(products, reason):
        '''Bulk updates products to unavailable status and updates EE if
        necessary.
        Keyword args:
        products - A list of models.Scene objects
        reason - The user facing reason the product was rejected
        '''
        product_ids = []
        for p in products:
            if isinstance(p, Scene):
                product_ids.append(p.id)
            else:
                raise TypeError()

        attrs = {'status': 'unavailable',
                'completion_date': datetime.datetime.now(),
                'note': reason}

        Scene.bulk_update(product_ids, attrs)
        # an exception will be raised in bulk_update
        # if it fails, so we shouldn't need to wrap
        # the lta call in a conditional
        for p in products:
            if p.order_attr('order_source') == 'ee':
                lta.update_order_status(p.order.ee_order_id, p.ee_unit_id, 'R')

        return True

    def update_status(self, name, orderid,
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
            with db_instance() as db:
                db.execute(sql)
                db.commit()
        except DBConnectException, e:
            message = "DBConnect Exception ordering_provider update_status sql: {0}\nmessage: {1}".format(sql, e.message)
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
            result = self.update_status(name, orderid, processing_loc=processing_loc, status=status)

        if action == 'set_product_error':
            result = self.set_product_error(name, orderid, processing_loc=processing_loc, error=error)

        if action == 'set_product_unavailable':
            result = self.set_product_unavailable(name, orderid,
                                                  processing_loc=processing_loc,
                                                  error=error, note=note)

        if action == 'mark_product_complete':
            result = self.mark_product_complete(name, orderid,
                                                processing_loc=processing_loc,
                                                completed_file_location=completed_file_location,
                                                destination_cksum_file=cksum_file_location,
                                                log_file_contents=log_file_contents)

        return result

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
            sql_list.append(" retry_after = '{0}', ".format(retry_after))
            sql_list.append(" log_file_contents = '{0}', ".format(error))
            sql_list.append(" processing_location = '{0}', ".format(processing_loc))
            sql_list.append(" note = '{0}'".format(note))
        else:
            print "****  problem in set_product_retry"
            raise ProductionProviderException("Exception Retry limit exceeded, name: {0}".format(name))

        sql_list.append(" where name = '{0}' AND order_id = {1};".format(name, order_id))
        sql = " ".join(sql_list)
        try:
            with db_instance() as db:
                db.execute(sql)
                db.commit()
        except DBConnectException, e:
            message = "DBConnectException set_product_retry. message: {0}\nsql: {1}".format(e.message, sql)
            raise ProductionProviderException(message)

        return True

    def set_product_error(self, name, orderid, processing_loc, error):
        ''' Marks a scene in error and accepts the log file contents '''

        order = Order.where("orderid = '{0}'".format(orderid))[0]
        product = Scene.where("name = '{0}' and order_id = '{1}'".format(name, order.id))[0]
        #attempt to determine the disposition of this error
        resolution = errors.resolve(error, name)

        if resolution is not None:

            if resolution.status == 'submitted':
                product.status = 'submitted'
                product.note = ''
                product.save()
            elif resolution.status == 'unavailable':
                self.set_product_unavailable(product.name,
                                        order.orderid,
                                        processing_loc,
                                        error,
                                        resolution.reason)
            elif resolution.status == 'retry':
                try:
                    self.set_product_retry(product.name,
                                      order.orderid,
                                      processing_loc,
                                      error,
                                      resolution.reason,
                                      resolution.extra['retry_after'],
                                      resolution.extra['retry_limit'])
                except Exception, e:
                    logger.debug("Exception setting {0} to retry:{1}"
                                 .format(name, e))
                    product.status = 'error'
                    product.processing_location = processing_loc
                    product.log_file_contents = error
                    product.save()
        else:
            product.status = 'error'
            product.processing_location = processing_loc
            product.log_file_contents = error
            product.save()

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
        buff.write('u.contactid, ')
        buff.write('s.name, ')
        buff.write('s.sensor_type, ')
        buff.write('o.orderid, ')
        buff.write('o.product_opts, ')
        buff.write('o.priority, ')
        buff.write('o.order_date, ')
        buff.write('q.running ')
        buff.write('FROM ordering_scene s ')
        buff.write('JOIN ordering_order o ON o.id = s.order_id ')
        buff.write('JOIN auth_user u ON u.id = o.user_id ')
        buff.write('LEFT JOIN order_queue q ON q.email = u.email ')
        buff.write('WHERE ')
        buff.write('o.status = \'ordered\' ')
        buff.write('AND s.status = \'oncache\' ')

        if product_types and len(product_types) > 0:
            ptypes = copy.deepcopy(product_types)

            # product_types comes in as a list from the transport layer
            if isinstance(ptypes, str):
                ptypes = ptypes.split(",")

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

        with db_instance() as db:
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

            logger.warn('Retrieved {0} modis urls for cid:{1}'.format(len(modis_urls), cid))
            for item in cid_items:
                dload_url = None
                if item['sensor_type'] == 'landsat':
                     # check to see if the product is still available

                    if ('status' in landsat_urls[item['name']] and
                            landsat_urls[item['name']]['status'] != 'available'):
                        try:
                            limit = config.get('retry.retry_missing_l1.retries')
                            timeout = int(config.get('retry.retry_missing_l1.timeout'))
                            ts = datetime.datetime.now()
                            after = ts + datetime.timedelta(seconds=timeout)

                            logger.info('{0} for order {1} was oncache '
                                        'but now unavailable, reordering'
                                        .format(item['name'], item['orderid']))

                            self.set_product_retry(item['name'],
                                              item['orderid'],
                                              'get_products_to_process',
                                              'product was not available',
                                              'reorder missing level1 product',
                                              after, limit)
                        except Exception:

                            logger.info('Retry limit exceeded for {0} in '
                                        'order {1}... moving to error status.'
                                        .format(item['name'], item['orderid']))

                            self.set_product_error(item['name'], item['orderid'],
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

                # Need to strip out everything not directly related to the scene
                options = self.strip_unrelated(item['name'], item['product_opts'])

                if config.get('convertprodopts') == 'True':
                    options = convert_options(options)

                result = {
                    'orderid': item['orderid'],
                    'product_type': item['sensor_type'],
                    'scene': item['name'],
                    'priority': item['priority'],
                    'options': options
                    #'options': json.loads(item['product_options'])
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

    @staticmethod
    def load_ee_orders():
        ''' Loads all the available orders from lta into
        our database and updates their status
        '''

        #check to make sure this operation is enabled.  Bail if not
        enabled = config.get("system.load_ee_orders_enabled")
        if enabled.lower() != 'true':
            logger.info('system.load_ee_orders_enabled is disabled,'
                        'skipping load_ee_orders()')
            return

        # This returns a dict that contains a list of dicts{}
        # key:(order_num, email, contactid) = list({sceneid:, unit_num:})
        orders = lta.get_available_orders()
        # print orders

        # use this to cache calls to EE Registration Service username lookups
        local_cache = {}

        # Capture in our db
        for eeorder, email_addr, contactid in orders:
            # create the orderid based on the info from the eeorder
            order_id = Order.generate_ee_order_id(email_addr, eeorder)
            order = Order.where("orderid = '{0}'".format(order_id))

            if not order:  # order is an empty list
                order = None
                # retrieve the username from the EE registration service
                # cache this call
                if contactid in local_cache:
                    username = local_cache[contactid]
                else:
                    username = lta.get_user_name(contactid)
                    local_cache[contactid] = username

                # Find or create the user
                db_id = User.find_or_create_user(username, email_addr, '', '', contactid)
                user = User.where('id = {}'.format(db_id))[0]

                # the contactid attr has been moved to the auth_user table
                if not user.contactid:
                    user.update('contactid', contactid)

                # We have a user now.  Now build the new Order since it
                # wasn't found.
                # TODO: This code should be housed in the models module.
                # TODO: This logic should not be visible at this level.
                order_dict = {}
                order_dict['orderid'] = order_id
                order_dict['user_id'] = user.id
                order_dict['order_type'] = 'level2_ondemand'
                order_dict['status'] = 'ordered'
                order_dict['note'] = 'EarthExplorer order id: %s' % eeorder
                order_dict['product_opts'] = Order.get_default_ee_options(
                    orders[eeorder, email_addr, contactid])
                order_dict['product_options'] = ''
                order_dict['ee_order_id'] = eeorder
                order_dict['order_source'] = 'ee'
                order_dict['order_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                order_dict['priority'] = 'normal'
                order_dict['email'] = user.email
                order = Order.create(order_dict)

            for s in orders[eeorder, email_addr, contactid]:
                #go look for the scene by ee_unit_id.  This will stop
                #duplicate key update collisions

                scene = None
                try:
                    scene_params = "order_id = {0} AND ee_unit_id = {1}".format(order.id, s['unit_num'])
                    scene = Scene.where(scene_params)[0]

                    if scene.status == 'complete':

                        success, msg, status =\
                            lta.update_order_status(eeorder, s['unit_num'], "C")

                        if not success:
                            log_msg = ("Error updating lta for "
                                       "[eeorder:%s ee_unit_num:%s "
                                       "scene name:%s order:%s to 'C' status")
                            log_msg = log_msg % (eeorder, s['unit_num'],
                                                 scene.name, order.orderid)

                            logger.error(log_msg)

                            log_msg = ("Error detail: lta return message:%s "
                                       "lta return status code:%s")
                            log_msg = log_msg % (msg, status)

                            logger.error(log_msg)

                    elif scene.status == 'unavailable':
                        success, msg, status =\
                            lta.update_order_status(eeorder, s['unit_num'], "R")

                        if not success:
                            log_msg = ("Error updating lta for "
                                       "[eeorder:%s ee_unit_num:%s "
                                       "scene name:%s order:%s to 'R' status")
                            log_msg = log_msg % (eeorder, s['unit_num'],
                                                 scene.name, order.orderid)

                            logger.error(log_msg)

                            log_msg = ("Error detail: "
                                       "lta return message:%s  lta return "
                                       "status code:%s") % (msg, status)

                            logger.error(log_msg)
                except IndexError:  # Scene does not exist
                    product = None
                    try:
                        product = sensor.instance(s['sceneid'])
                    except Exception:
                        log_msg = ("Received product via EE that "
                                   "is not implemented: %s" % s['sceneid'])
                        logger.debug(log_msg)
                        continue
                        # raise ProductionProviderException("Cant find sensor instance. {0}".format(log_msg))

                    sensor_type = ""

                    if isinstance(product, sensor.Landsat):
                        sensor_type = 'landsat'
                    elif isinstance(product, sensor.Modis):
                        sensor_type = 'modis'

                    scene_dict = {}
                    scene_dict['name'] = product.product_id
                    scene_dict['order_id'] = order.id
                    scene_dict['status'] = 'submitted'
                    scene_dict['sensor_type'] = sensor_type
                    scene_dict['ee_unit_id'] = s['unit_num']
                    # order_date isn't an column on the ordering_scene table
                    # will leave commented out
                    #scene_dict['order_date']= datetime.datetime.now()

                    Scene.create(scene_dict)

                # Update LTA
                success, msg, status = lta.update_order_status(eeorder, s['unit_num'], "I")

                if not success:
                    log_msg = ("Error updating lta for "
                               "[eeorder:%s ee_unit_num:%s scene "
                               "name:%s order:%s to 'I' status "
                               "lta return message: %s"
                               "lta return status code: %s") % (eeorder, s['unit_num'],
                                                                s['sceneid'], order.orderid,
                                                                msg, status)
                    logger.error(log_msg)


    def handle_retry_products(self):
        ''' handles all products in retry status '''
        now = datetime.datetime.now()
        filters = ["status = 'retry'",
                   "retry_after < '{0}'".format(now)]

        products = Scene.where(filters)
        if len(products) > 0:
            Scene.bulk_update([p.id for p in products], {'status': 'submitted', 'note': ''})

    def handle_onorder_landsat_products(self):
        ''' handles landsat products still on order '''

        filters = "tram_order_id IS NOT NULL AND status = 'onorder'"

        products = Scene.where(filters)
        product_tram_ids = [product.tram_order_id for product in products]

        rejected = []
        available = []

        for tid in product_tram_ids:
            order_status = lta.get_order_status(tid)

            # There are a variety of product statuses that come back from tram
            # on this call.  I is inprocess, Q is queued for the backend system,
            # D is duplicate, C is complete and R is rejected.  We are ignoring
            # all the statuses except for R and C because we don't care.
            # In the case of D (duplicates), when the first product completes, all
            # duplicates will also be marked C
            for unit in order_status['units']:
                if unit['unit_status'] == 'R':
                    rejected.append(unit['sceneid'])
                elif unit['unit_status'] == 'C':
                    available.append(unit['sceneid'])

        # Go find all the tram units that were rejected and mark them
        # unavailable in our database.  Note that we are not looking for
        # specific tram_order_id/sceneids as duplicate tram orders may have been
        # submitted and we want to bulk update all scenes that are onorder but
        # have been rejected
        if len(rejected) > 0:
            rejected_products = [p for p in products if p.name in rejected]
            self.set_products_unavailable(rejected_products,
                                          'Level 1 product could not be produced')

        # Now update everything that is now on cache
        filters = "status = 'onorder' AND name in {0}".format(tuple(available))
        # pull the trailing comma for single item tuples
        filters = filters.replace(",)", ")")

        if len(available) > 0:
            products = Scene.where(filters)
            Scene.bulk_update([p.id for p in products], {'status': 'oncache', 'note': ''})

        return True

    def send_initial_emails(self):
        return emails.Emails().send_all_initial()

    def get_contactids_for_submitted_landsat_products(self):
        logger.info("Retrieving contact ids for submitted landsat products")

        scenes = Scene.where("status = 'submitted' AND sensor_type = 'landsat'")
        user_ids = [s.order_attr('user_id') for s in scenes]
        users = User.where("id in {0}".format(tuple(user_ids)))
        contact_ids = set([user.contactid for user in users])

        logger.info("Found contact ids:{0}".format(contact_ids))
        return contact_ids

    def update_landsat_product_status(self, contact_id):
        ''' updates the product status for all landsat products for the
        ee contact id '''
        logger.info("Updating landsat product status")

        user = User.where("contactid = '{0}'".format(contact_id))[0]
        product_list = Order.get_user_scenes(user.id, ["sensor_type = 'landsat' AND status = 'submitted'"])

        logger.info("Ordering {0} scenes for contact:{1}"
                     .format(len(product_list), contact_id))

        results = lta.order_scenes(product_list, contact_id)

        logger.info("Checking ordering results for contact:{0}"
                     .format(contact_id))

        if 'available' in results and len(results['available']) > 0:
            available_product_ids = [product.id for product in product_list if product.name in results['available']]
            Scene.bulk_update(available_product_ids, {"status":"oncache", "note":"''"})

        if 'ordered' in results and len(results['ordered']) > 0:
            ordered_product_ids = [product.id for product in product_list if product.name in results['ordered']]
            Scene.bulk_update(ordered_product_ids, {"status":"onorder", "tram_order_id":results['lta_order_id'], "note":"''"})

        if 'invalid' in results and len(results['invalid']) > 0:
            #look to see if they are ee orders.  If true then update the
            #unit status

            invalid = [p for p in product_list if p.name in results['invalid']]

            self.set_products_unavailable(invalid, 'Not found in landsat archive')

        return True

    def mark_nlaps_unavailable(self):
        ''' inner function to support marking nlaps products unavailable '''
        logger.info("Looking for submitted landsat products, In mark_nlaps_unavailable")
        #First things first... filter out all the nlaps scenes
        filter = "status = 'submitted' AND sensor_type = 'landsat'"
        landsat_products = Scene.where(filter)
        landsat_submitted = [l.name for l in landsat_products]

        logger.info("Found {0} submitted landsat products"
                     .format(len(landsat_submitted)))

        # find all the submitted products that are nlaps and reject them
        logger.info("Checking for TMA data in submitted landsat products")
        landsat_nlaps = nlaps.products_are_nlaps(landsat_submitted)

        landsat_submitted = None

        logger.info("Found {0} landsat TMA products".format(len(landsat_nlaps)))

        # bulk update the nlaps scenes
        if len(landsat_nlaps) > 0:
            _nlaps = [p for p in landsat_products if p.name in landsat_nlaps]
            landsat_nlaps = None
            self.set_products_unavailable(_nlaps, 'TMA data cannot be processed')

        return True

    def handle_submitted_landsat_products(self):
        ''' handles all submitted landsat products '''
        logger.info('Handling submitted landsat products...')

        #Here's the real logic for this handling submitted landsat products
        self.mark_nlaps_unavailable()

        for contact_id in self.get_contactids_for_submitted_landsat_products():
            try:
                logger.info("Updating landsat_product_status for {0}"
                            .format(contact_id))

                self.update_landsat_product_status(contact_id)

            except Exception, e:
                msg = ('Could not update_landsat_product_status for {0}\n'
                       'Exception:{1}'.format(contact_id, e))
                logger.exception(msg)

        return True

    def handle_submitted_modis_products(self):
        ''' Moves all submitted modis products to oncache if true '''

        logger.info("Handling submitted modis products...")

        modis_products = Scene.where("status = 'submitted' AND sensor_type = 'modis'")

        logger.warn("Found {0} submitted modis products"
                     .format(len(modis_products)))

        if len(modis_products) > 0:
            lpdaac_ids = []
            nonlp_ids = []

            for product in modis_products:
                if lpdaac.input_exists(product.name) is True:
                    lpdaac_ids.append(product.id)
                    logger.warn('{0} is on cache'.format(product.name))
                else:
                    nonlp_ids.append(product.id)
                    logger.warn('{0} was not found in the modis data pool'
                                 .format(product.name))

            if lpdaac_ids:
                Scene.bulk_update(lpdaac_ids, {"status":"oncache"})
            if nonlp_ids:
                Scene.bulk_update(nonlp_ids, {"status":"unavailable", "note":"not found in modis data pool"})

        return True

    def handle_submitted_plot_products(self):
        ''' Moves plot products from submitted to oncache status once all
            their underlying rasters are complete or unavailable '''

        logger.info("Handling submitted plot products...")

        plot_orders = Order.where("status = 'ordered' AND order_type = 'lpcs'")

        logger.info("Found {0} submitted plot orders"
                     .format(len(plot_orders)))

        for order in plot_orders:
            products = order.scenes()
            product_count = len(products)

            complete_products = order.scenes(["status = 'complete'"])
            complete_count = len(complete_products)

            unavailable_products = order.scenes(["status = 'unavailable'"])
            unavailable_count = len(unavailable_products)

            #if this is an lpcs order and there is only 1 product left that
            #is not done, it must be the plot product.  Will verify this
            #in next step.  Plotting cannot run unless everything else
            #is done.

            #logger.info("product_count = {0}".format(product_count))
            #logger.info("unavailable_count = {0}".format(unavailable_count))
            #logger.info("complete_count = {0}".format(complete_count))

            if product_count - (unavailable_count + complete_count) == 1:
                plot = order.scenes(["status = 'submitted'", "sensor_type = 'plot'"])
                if len(plot) >= 1:
                    for p in plot:
                        if complete_count == 0:
                            p.status = 'unavailable'
                            note = 'No input products were available for '\
                                    'plotting and statistics'
                            p.note = note
                            logger.info('No input products available for '
                                         'plotting in order {0}'
                                         .format(order.orderid))
                        else:
                            p.status = 'oncache'
                            p.note = ''
                            logger.info("{0} plot is on cache"
                                         .format(order.orderid))
                        p.save()
        return True

    def handle_submitted_products(self):
        ''' handles all submitted products in the system '''

        logger.info('Handling submitted products...')
        self.handle_submitted_landsat_products()
        self.handle_submitted_modis_products()
        self.handle_submitted_plot_products()
        return True

    def send_completion_email(self, order):
        ''' public interface to send the completion email '''
        return emails.Emails().send_completion(order)

    def update_order_if_complete(self, order):
        '''Method to send out the order completion email
        for orders if the completion of a scene
        completes the order

        Keyword args:
        orderid -- id of the order

        '''
        if type(order) == str:
            #will raise Order.DoesNotExist
            order = Order.where("orderid = '{0}'".format(order))[0]
        elif type(order) == int:
            order = Order.where("id = {0}".format(order))[0]

        if not type(order) == Order:
            msg = "%s must be of type Order, int or str" % order
            raise TypeError(msg)

        # find all scenes that are not complete
        scenes = order.scenes(["status NOT IN ('complete', 'unavailable')"])
        if len(scenes) == 0:

            logger.info('Completing order: {0}'.format(order.orderid))
            order.status = 'complete'
            order.completion_date = datetime.datetime.now()
            order.save()
            #only send the email if this was an espa order.
            if order.order_source == 'espa' and not order.completion_email_sent:
                try:
                    sent = None
                    sent = self.send_completion_email(order)
                    if sent is None:
                        logger.debug('Completeion email not sent for {0}'
                                         .format(order.orderid))
                        raise Exception("Completion email not sent")
                    else:
                        order.completion_email_sent = datetime.datetime.now()
                        order.save()
                except Exception, e:
                    #msg = "Error calling send_completion_email:{0}".format(e)
                    logger.debug('Error calling send_completion_email')
                    raise e
        return True

    def finalize_orders(self):
        '''Checks all open orders in the system and marks them complete if all
        required scene processing is done'''

        orders = Order.where("status = 'ordered'")
        [self.update_order_if_complete(o) for o in orders]
        return True

    def purge_orders(self, send_email=False):
        ''' Will move any orders older than X days to purged status and will also
        remove the files from disk'''

        days = config.get('policy.purge_orders_after')

        logger.info('Using purge policy of {0} days'.format(days))

        cutoff = datetime.datetime.now() - datetime.timedelta(days=int(days))

        orders = Order.where("status = 'complete' AND completion_date < '{0}'".format(cutoff))

        logger.info('Purging {0} orders from the active record.'
            .format(len(orders)))

        start_capacity = onlinecache.capacity()
        logger.info('Starting cache capacity:{0}'.format(start_capacity))

        for order in orders:
            try:
                #with transaction.atomic():
                order.update('status', 'purged')
                for product in order.scenes():
                    product.status = 'purged'
                    product.log_file_contents = ''
                    product.product_distro_location = ''
                    product.product_dload_url = ''
                    product.cksum_distro_location = ''
                    product.cksum_download_url = ''
                    product.job_name = ''
                    product.save()

                # bulk update product status, delete unnecessary field data
                logger.info('Deleting {0} from online cache disk'.format(order.orderid))

                onlinecache.delete(order.orderid)
            except onlinecache.OnlineCacheException:
                logger.debug('Could not delete {0} from the online cache'.format(order.orderid))
            except Exception:
                logger.debug('Exception purging {0}'.format(order.orderid))

        end_capacity = onlinecache.capacity()
        logger.info('Ending cache capacity:{0}'.format(end_capacity))

        if send_email is True:
            logger.info('Sending purge report')
            emails.send_purge_report(start_capacity, end_capacity, orders)

        return True

    def handle_orders(self):
        '''Logic handler for how we accept orders + products into the system'''
        self.send_initial_emails()
        self.handle_onorder_landsat_products()
        self.handle_retry_products()
        self.load_ee_orders()
        self.handle_submitted_products()
        self.finalize_orders()

        cache_key = 'orders_last_purged'
        result = cache.get(cache_key)

        # dont run this unless the cached lock has expired
        if result is None:
            logger.info('Purge lock expired... running')

            # first thing, populate the cached lock field
            timeout = int(config.get('system.run_order_purge_every'))
            cache.set(cache_key, datetime.datetime.now(), timeout)

            #purge the orders from disk now
            self.purge_orders(send_email=True)
        else:
            logger.info('Purge lock detected... skipping')
        return True

    def strip_unrelated(self, sceneid, opts):
        opts = copy.deepcopy(opts)

        short = sensor.instance(sceneid).shortname
        sen_keys = sensor.SensorCONST.instances.keys()
        opts['products'] = opts[short]['products']

        for sen in sen_keys:
            if sen in opts:
                opts.pop(sen)

        return opts
