from api.domain import sensor
from api.domain.scene import Scene, SceneException
from api.domain.order import Order, OptionsConversion, OrderException
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.util.dbconnect import DBConnectException, db_instance
from api.providers.production import ProductionProviderInterfaceV0
from api.providers.caching.caching_provider import CachingProvider
from api.external import lpdaac, lta, onlinecache, nlaps, hadoop
from api.system import errors
from api.notification import emails
from api.domain.user import User

import copy
import datetime
import urllib
import json
import socket
import os
import yaml

from cStringIO import StringIO

from api.system.logger import ilogger as logger

config = ConfigurationProvider()
cache = CachingProvider()
hadoop_handler = hadoop.HadoopHandler()


class ProductionProviderException(Exception):
    pass


class ProductionProvider(ProductionProviderInterfaceV0):

    def queue_products(self, order_name_tuple_list, processing_location, job_name):
        """
        Allows the caller to place products into queued status in bulk
        :param order_name_tuple_list: list of tuples, ie [(orderid, scene_name), ...]
        :param processing_location: location of request to queue products
        :param job_name: name of job
        :return: True
        """
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
            product_tup = tuple(str(p) for p in orders[order])
            order = Order.find(order)

            scenes = Scene.where({'order_id': order.id, 'name': product_tup})
            updates = {"status": "queued",
                       "processing_location": processing_location,
                       "log_file_contents": "''",
                       "note": "''",
                       "job_name": job_name}

            Scene.bulk_update([s.id for s in scenes], updates)

        return True

    def mark_product_complete(self, name, orderid, processing_loc=None,
                              completed_file_location=None,
                              destination_cksum_file=None,
                              log_file_contents=None):
        """
        Mark a scene complete
        :param name: name of scene
        :param orderid: order id of scene
        :param processing_loc: where request originated
        :param completed_file_location: where completed product was stored
        :param destination_cksum_file: where product cksum file was stored
        :param log_file_contents: log file contents from processing
        :return: True
        """

        order_id = Scene.get('order_id', name, orderid)
        order_source = Scene.get('order_source', name, orderid)
        base_url = config.url_for('distribution.cache')

        product_file_parts = completed_file_location.split('/')
        product_file = product_file_parts[len(product_file_parts) - 1]
        cksum_file_parts = destination_cksum_file.split('/')
        cksum_file = cksum_file_parts[len(cksum_file_parts) - 1]

        product_dload_url = ('{}/orders/{}/{}'
                             .format(base_url, orderid, product_file))
        cksum_download_url = ('{}/orders/{}/{}'
                              .format(base_url, orderid, cksum_file))

        scene = Scene.by_name_orderid(name, order_id)
        scene.status = 'complete'
        scene.processing_location = processing_loc
        scene.product_distro_location = completed_file_location
        scene.completion_date = datetime.datetime.now()
        scene.cksum_distro_location = destination_cksum_file
        scene.log_file_contents = log_file_contents
        scene.product_dload_url = product_dload_url
        scene.cksum_download_url = cksum_download_url
        try:
            scene.download_size = os.path.getsize(completed_file_location)
        except OSError, e:
            raise ProductionProviderException('Could not find completed file location')

        if order_source == 'ee':
            # update EE
            ee_order_id = Scene.get('ee_order_id', name, orderid)
            ee_unit_id = Scene.get('ee_unit_id', name, orderid)
            try:
                lta.update_order_status(ee_order_id, ee_unit_id, 'C')
            except Exception, e:
                # perhaps this doesn't need to be elevated to 'debug' status
                # as its a fairly regular occurrence
                logger.debug('Problem updating LTA order: {}'.format(e))
                scene.failed_lta_status_update = 'C'

        try:
            scene.save()
        except DBConnectException, e:
            message = "DBConnect Exception ordering_provider mark_product_complete scene: {0}"\
                        "\nmessage: {1}".format(scene, e.message)
            raise OrderException(message)

        return True

    def set_product_unavailable(self, name, orderid,
                                processing_loc=None, error=None, note=None):
        """
        Set a product unavailable
        :param name: name of scene to mark unavailable
        :param orderid: order id of scene to mark unavailable
        :param processing_loc: where call to mark scene unavailable originated
        :param error: error message
        :param note: note
        :return: True
        """

        order_id = Scene.get('order_id', name, orderid)
        order_source = Scene.get('order_source', name, orderid)

        scene = Scene.by_name_orderid(name, order_id)
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
            try:
                lta.update_order_status(ee_order_id, ee_unit_id, 'R')
            except Exception, e:
                # perhaps this doesn't need to be elevated to 'debug' status
                # as its a fairly regular occurrence
                logger.debug('Problem updating LTA order: {}'.format(e))
                scene.failed_lta_status_update = 'R'

        try:
            scene.save()
        except DBConnectException, e:
            message = "DBConnect Exception ordering_provider set_product_unavailable " \
                      "scene: {0}\nmessage: {1}".format(scene, e.message)
            raise ProductionProviderException(message)

        return True

    @staticmethod
    def set_products_unavailable(products, reason):
        """
        Bulk updates products to unavailable status and updates EE if
        necessary.
        :param products: list of Scene objects
        :param reason: user facing explanation for why request was rejected
        :return: True
        """
        try:
            Scene.bulk_update([p.id for p in products],
                              {'status': 'unavailable',
                               'completion_date': datetime.datetime.now(),
                               'note': reason})
            for p in products:
                if p.order_attr('order_source') == 'ee':
                    try:
                        lta.update_order_status(p.order_attr('ee_order_id'), p.ee_unit_id, 'R')
                    except Exception, e:
                        # perhaps this doesn't need to be elevated to 'debug' status
                        # as its a fairly regular occurrence
                        logger.debug('Problem updating LTA order: {}'.format(e))
                        p.update('failed_lta_status_update', 'R')
        except Exception, e:
            raise ProductionProviderException(e)

        return True

    def update_status(self, name, orderid, processing_loc=None, status=None):
        """
        Update the status for a scene give its name, and order_id
        :param name: name of scene to update
        :param orderid: the order id of scene to update
        :param processing_loc: where in processing the status is being updated from
        :param status: what the status is to be set to
        :return: True
        """
        order = Order.find(orderid)
        scene = Scene.by_name_orderid(name, order.id)
        if processing_loc:
            scene.processing_location = processing_loc
        if status:
            scene.status = status
        scene.save()
        log_str = "Scene status updated. order: {0}\n scene id/name: {1}/{2}\nstatus:{3}\nprocessing_location{4}\n "
        logger.info(log_str.format(order.orderid, scene.id, scene.name, scene.status, scene.processing_location))
        return True

    def update_product(self, action, name=None, orderid=None,
                       processing_loc=None, status=None, error=None,
                       note=None, completed_file_location=None,
                       cksum_file_location=None, log_file_contents=None):
        """
        Update a scene's status to error, unavailable, complete, or something else

        :param action: name of the action to perform
        :param name: name of the scene to perform action on
        :param orderid: order id of the scene to perform action on
        :param processing_loc: where the request to perform the action came from
        :param status: new scene status
        :param error: new error message
        :param note: new note value
        :param completed_file_location: where finished product is stored
        :param cksum_file_location: where cksum file for product is stored
        :param log_file_contents: new log file contents
        :return: True
        """
        if action == 'update_status':
            result = self.update_status(name, orderid,
                                        processing_loc=processing_loc,
                                        status=status)

        elif action == 'set_product_error':
            result = self.set_product_error(name, orderid,
                                            processing_loc=processing_loc,
                                            error=error)

        elif action == 'set_product_unavailable':
            result = self.set_product_unavailable(name, orderid,
                                                  processing_loc=processing_loc,
                                                  error=error, note=note)

        elif action == 'mark_product_complete':
            result = self.mark_product_complete(name, orderid,
                                                processing_loc=processing_loc,
                                                completed_file_location=completed_file_location,
                                                destination_cksum_file=cksum_file_location,
                                                log_file_contents=log_file_contents)

        else:
            result = {'msg': ('{} is not an accepted action for '
                              'update_product'.format(action))}

        return result

    def set_product_retry(self, name, orderid, processing_loc,
                          error, note, retry_after, retry_limit=None):
        """
        Set a product into retry status

        :param name: scene/collection name
        :param orderid: order id, longname
        :param processing_loc: processing computer name
        :param error: error log
        :param note: note to update
        :param retry_after: retry after given timestamp
        :param retry_limit: maximum number of tries
        """
        order = Order.find(orderid)
        scene = Scene.by_name_orderid(name, order.id)

        retry_count = scene.retry_count if scene.retry_count else 0

        if not retry_limit:
            retry_limit = scene.retry_limit

        # make sure retry_limit and retry_count are ints
        retry_count = int(retry_count)
        retry_limit = int(retry_limit)
        new_retry_count = retry_count + 1

        if new_retry_count > retry_limit:
            raise ProductionProviderException('Retry limit exceeded, name: {}'.format(name))

        scene.status = 'retry'
        scene.retry_count = new_retry_count
        scene.retry_after = retry_after
        scene.retry_limit = retry_limit
        scene.log_file_contents = error
        scene.processing_location = processing_loc
        scene.note = note
        scene.save()

        return True

    def set_product_error(self, name, orderid, processing_loc, error):
        """
        Marks a scene in error and accepts the log file contents
        :param name: name of scene to update
        :param orderid: order id of scene to update
        :param processing_loc: where command to update scene came from
        :param error: error message from processing
        :return: True
        """
        order = Order.find(orderid)
        product = Scene.by_name_orderid(name, order.id)
        #attempt to determine the disposition of this error
        resolution = None
        if name != 'plot':
            resolution = errors.resolve(error, name)

        logger.info("\n\n*** set_product_error: orderid {0}, "
                    "scene id {1} , scene name {2},\n"
                    "error {4},\n"
                    "resolution {3}\n\n".format(order.orderid, product.id,
                                                product.name, resolution, error))

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
                except Exception as e:
                    logger.info('Exception setting product.id {} {} '
                                 'to retry: {}'
                                 .format(product.id, name, e))
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
        """
        Find scenes that are oncache and return them as properly formatted
        json per the interface description between the web and processing tier
        :param record_limit: max number of scenes to retrieve
        :param for_user: the user whose scenes to retrieve
        :param priority: the priority of scenes to retrieve
        :param product_types: types of products to retrieve
        :param encode_urls: whether to encode the urls
        :return: list
        """
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
            if isinstance(ptypes, basestring):
                # ptypes is unicode values of either: u"['plot']" or u"['landsat', 'modis']"
                ptypes = eval(ptypes)

            type_str = ','.join('\'{0}\''.format(x) for x in ptypes)
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
                            after = after.strftime('%Y-%m-%d %H:%M:%S.%f')

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

                if item['name'] == 'plot':
                    options = {}
                elif config.get('convertprodopts') == 'True':
                    options = OptionsConversion.convert(new=item['product_opts'],
                                                        scenes=[item['name']])
                else:
                    # Need to strip out everything not directly related to the scene
                    options = self.strip_unrelated(item['name'], item['product_opts'])

                result = {
                    'orderid': item['orderid'],
                    'product_type': item['sensor_type'],
                    'scene': item['name'],
                    'priority': item['priority'],
                    'options': options
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

    def load_ee_orders(self):
        """
        Loads all the available orders from lta into
        our database and updates their status
        """
        # Check to make sure this operation is enabled.  Bail if not
        enabled = config.get('system.load_ee_orders_enabled')
        if enabled.lower() == 'false':
            logger.info('system.load_ee_orders_enabled is disabled,'
                        'skipping load_ee_orders()')
            return

        orders = lta.get_available_orders()

        # {(order_num, email, contactid): [{sceneid: ,
        #                                   unit_num:}]}
        for eeorder, email_addr, contactid in orders:
            # create the orderid based on the info from the eeorder
            order_id = Order.generate_ee_order_id(email_addr, eeorder)

            order = Order.find(order_id)
            scene_info = orders[eeorder, email_addr, contactid]

            if order:
                # EE order already exists in the system
                # update the associated scenes
                self.update_ee_orders(scene_info, eeorder, order.id)
                #continue

            else:
                cache_key = '-'.join(['load_ee_orders', str(contactid)])
                user = cache.get(cache_key)

                if user is None:
                    username = lta.get_user_name(contactid)
                    # Find or create the user
                    db_id = User.find_or_create_user(username, email_addr,
                                                     'from', 'earthexplorer',
                                                     contactid)
                    user = User.find(db_id)
                    if not user.contactid:
                        user.update('contactid', contactid)

                    cache.set(cache_key, user, 60)

                # We have a user now.  Now build the new Order since it
                # wasn't found
                ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                order_dict = {'orderid': order_id,
                              'user_id': user.id,
                              'order_type': 'level2_ondemand',
                              'status': 'ordered',
                              'note': 'EarthExplorer order id: {}'.format(eeorder),
                              'ee_order_id': eeorder,
                              'order_source': 'ee',
                              'order_date': ts,
                              'priority': 'normal',
                              'email': user.email,
                              'product_options': 'include_sr: true',
                              'product_opts': Order.get_default_ee_options(scene_info)}

                order = Order.create(order_dict)
                self.load_ee_scenes(scene_info, order.id)
                self.update_ee_orders(scene_info, eeorder, order.id)

    @staticmethod
    def gen_ee_scene_list(ee_scenes, order_id):
        """
        Return formatted list of dictionaries used to insert
        scene records from EE orders

        ee_scenes = [{'sceneid': xxx , 'unit_num': iii }]

        :param ee_scenes: list of scenes to insert into the db
        :param order_id: the id of the order the scenes belong to
        :return: list of dictionaries, used for generating scene records
        """
        bulk_ls = []
        for s in ee_scenes:
            product = sensor.instance(s['sceneid'])

            sensor_type = ''
            if isinstance(product, sensor.Landsat):
                sensor_type = 'landsat'
            elif isinstance(product, sensor.Modis):
                sensor_type = 'modis'

            status = 'submitted'
            note = ''
            # All EE orders are for SR, require auxiliary data
            if product.sr_date_restricted():
                status = 'unavailable'
                note = 'auxiliary data unavailable for' \
                       'this scenes acquisition date'

            scene_dict = {'name': product.product_id,
                          'sensor_type': sensor_type,
                          'order_id': order_id,
                          'status': status,
                          'note': note,
                          'ee_unit_id': s['unit_num']}

            bulk_ls.append(scene_dict)
        return bulk_ls

    def load_ee_scenes(self, ee_scenes, order_id, missed=None):
        """
        Load the associated EE scenes into the system for processing

        ee_scenes_example = [{'sceneid': xxx, 'unit_num': iii}]

        :param ee_scenes: list of scenes to place in the DB
        :param order_id: numeric ordering_order.id associated with the
          scenes
        :param missed: used to indicate adding missing scenes to existing
          order
        """
        bulk_ls = self.gen_ee_scene_list(ee_scenes, order_id)
        try:
            Scene.create(bulk_ls)
        except (SceneException, sensor.ProductNotImplemented) as e:
            if missed:
                # we failed to load scenes missed on initial EE order import
                # we do not want to delete the order, as we would on initial
                # creation
                logger.debug('EE Scene creation failed on scene injection, '
                             'for missing EE scenes on existing order '
                             'order: {}\nexception: {}'.format(order_id, e.message))
            else:
                logger.debug('EE Order creation failed on scene injection, '
                             'order: {}\nexception: {}'
                             .format(order_id, e.message))

                with db_instance() as db:
                    db.execute('delete ordering_order where id = %s',
                               order_id)
                    db.commit()

            raise ProductionProviderException(e)

    def update_ee_orders(self, ee_scenes, eeorder, order_id):
        """
        Update the LTA tracking system with the current status of
        a product in the system

        ee_scenes_example = [{'sceneid': ,
                              'unit_num': }]

        :param ee_scenes: list of dicts
        :param eeorder: associated EE order id
        :param order_id: order id used in the system
        """
        missing_scenes = []
        for s in ee_scenes:
            scene = Scene.where({'order_id': order_id, 'ee_unit_id': s['unit_num']})

            if scene:
                scene = scene[0]
                if scene.status == 'complete':
                    status = 'C'
                elif scene.status == 'unavailable':
                    status = 'R'
                else:
                    status = 'I'
                try:
                    lta.update_order_status(eeorder, s['unit_num'], status)
                except Exception, e:
                    logger.debug("Error updating lta for scene: {}\n{}".format(scene.id, e))
                    scene.update('failed_lta_status_update', status)
            else:
                # scene insertion was missed initially, add it now
                missing_scenes.append(s)

        if missing_scenes:
            # There appear to be scenes in this order which we didn't receive the
            # first go around, try adding them now
            order = Order.find(order_id)
            order.update('product_opts', json.dumps(Order.get_default_ee_options(ee_scenes)))

            self.load_ee_scenes(missing_scenes, order_id, missed=True)

    def handle_retry_products(self):
        """
        Handle all products in retry status
        :return: True
        """
        try:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            products = Scene.where({'status': 'retry', 'retry_after <': now})
            if len(products) > 0:
                Scene.bulk_update([p.id for p in products], {'status': 'submitted', 'note': ''})
        except Exception as e:
            raise ProductionProviderException("error with handle_retry_products: {}".format(e))

        return True

    def handle_onorder_landsat_products(self):
        """
        Handles landsat products still on order
        :return: True
        """
        products = Scene.where({'status': 'onorder', 'tram_order_id IS NOT': None})

        # lets control how many scenes were going to ping LTA for status updates
        # every 7 (currently) minutes
        # tram_order_id is sequential (looks like a timestamp), so we can sort
        # by that, running with the 'oldest' orders assuming they process FIFO
        product_tram_ids = set([product.tram_order_id for product in products])
        sorted_tram_ids = sorted(product_tram_ids)[:500]

        rejected = []
        available = []

        # converting to a set eliminates duplicate calls to lta
        for tid in sorted_tram_ids:
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
            # scene may not be rejected or complete
            if rejected_products:
                self.set_products_unavailable(rejected_products, 'Level 1 product could not be produced')

        if len(available) > 0:
            products = Scene.where({'status': 'onorder', 'name': tuple(available)})
            # scene may not be rejected or complete
            if products:
                Scene.bulk_update([p.id for p in products], {'status': 'oncache', 'note': ''})

        return True

    def send_initial_emails(self):
        """
        ProductionProvider wrapper for Emails.send_all_initial
        :return: True
        """
        return emails.Emails().send_all_initial()

    @staticmethod
    def get_contactids_for_submitted_landsat_products():
        """
        Assembles a list of contactids for submitted landsat products
        :return: list
        """
        logger.info("Retrieving contact ids for submitted landsat products")
        scenes = Scene.where({'status': 'submitted',
                              'sensor_type': 'landsat'})

        if scenes:
            user_ids = [s.order_attr('user_id') for s in scenes]
            users = User.where({'id': tuple(user_ids)})
            contact_ids = set([user.contactid for user in users])
            logger.info("Found contact ids:{0}".format(contact_ids))
            return contact_ids
        else:
            return []

    def update_landsat_product_status(self, contact_id):
        """
        Updates the product status for all landsat products for the EE contact id
        :param contact_id:
        :return: True
        """
        logger.info("Updating landsat product status")
        user = User.by_contactid(contact_id)
        product_list = Order.get_user_scenes(user.id, {'sensor_type': 'landsat','status': 'submitted'})[:500]
        logger.info("Ordering {0} scenes for contact:{1}".format(len(product_list), contact_id))

        prod_name_list = [p.name for p in product_list]
        results = lta.order_scenes(prod_name_list, contact_id)

        logger.info("Checking ordering results for contact:{0}".format(contact_id))

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
        """
        Inner function to support marking nlaps products unavailable
        :return: True
        """
        logger.info("Looking for submitted landsat products, In mark_nlaps_unavailable")

        # First things first... filter out all the nlaps scenes
        landsat_products = Scene.where({'status': 'submitted', 'sensor_type': 'landsat'})
        landsat_submitted = [l.name for l in landsat_products]
        logger.info("Found {0} submitted landsat products".format(len(landsat_submitted)))

        # find all the submitted products that are nlaps and reject them
        logger.info("Checking for TMA data in submitted landsat products")
        landsat_nlaps = nlaps.products_are_nlaps(landsat_submitted)
        logger.info("Found {0} landsat TMA products".format(len(landsat_nlaps)))

        # bulk update the nlaps scenes
        if len(landsat_nlaps) > 0:
            _nlaps = [p for p in landsat_products if p.name in landsat_nlaps]
            self.set_products_unavailable(_nlaps, 'TMA data cannot be processed')

        return True

    def handle_submitted_landsat_products(self):
        """
        Handles all submitted landsat products
        :return: True
        """
        logger.info('Handling submitted landsat products...')
        # Here's the real logic for this handling submitted landsat products
        self.mark_nlaps_unavailable()

        contactids = self.get_contactids_for_submitted_landsat_products()

        for contact_id in contactids:
            if contact_id:
                try:
                    logger.info("Updating landsat_product_status for {0}"
                                .format(contact_id))
                    self.update_landsat_product_status(contact_id)

                except Exception, e:
                    msg = ('Could not update_landsat_product_status for {0}\n'
                           'Exception:{1}'.format(contact_id, e))
                    logger.debug(msg)

        return True

    def handle_submitted_modis_products(self):
        """
        Moves all submitted modis products to oncache if true
        :return: True
        """
        logger.info("Handling submitted modis products...")
        modis_products = Scene.where({'status': 'submitted', 'sensor_type': 'modis'})
        logger.warn("Found {0} submitted modis products".format(len(modis_products)))

        if len(modis_products) > 0:
            lpdaac_ids = []
            nonlp_ids = []

            for product in modis_products:
                if lpdaac.input_exists(product.name) is True:
                    lpdaac_ids.append(product.id)
                    logger.warn('{0} is on cache'.format(product.name))
                else:
                    nonlp_ids.append(product.id)
                    logger.warn('{0} was not found in the modis data pool'.format(product.name))

            if lpdaac_ids:
                Scene.bulk_update(lpdaac_ids, {"status": "oncache"})
            if nonlp_ids:
                Scene.bulk_update(nonlp_ids, {"status":"unavailable", "note":"not found in modis data pool"})

        return True

    def handle_submitted_plot_products(self):
        """
        Moves plot products from submitted to oncache status once all their underlying rasters are complete
        or unavailable
        :return: True
        """
        logger.info("Handling submitted plot products...")
        plot_scenes = Scene.where({'status': 'submitted', 'sensor_type': 'plot'})
        plot_orders = [Order.find(s.order_id) for s in plot_scenes]
        logger.info("Found {0} submitted plot orders".format(len(plot_orders)))

        for order in plot_orders:
            product_count = order.scene_status_count()
            complete_count = order.scene_status_count('complete')
            unavailable_count = order.scene_status_count('unavailable')

            # if there is only 1 product left that is not done, it must be
            # the plot product. Will verify this in next step.  Plotting
            # cannot run unless everything else is done.
            log_msg = "plot product_count = {}\nplot unavailable count = {}\nplot complete count{}"
            logger.info(log_msg.format(product_count, unavailable_count, complete_count))

            if product_count - (unavailable_count + complete_count) == 1:
                if len(plot_scenes) >= 1:
                    for p in plot_scenes:
                        if complete_count == 0:
                            p.status = 'unavailable'
                            p.note = 'No input products were available for plotting and statistics'
                            logger.info('No input products available for '
                                        'plotting in order {0}'.format(order.orderid))
                        else:
                            p.status = 'oncache'
                            p.note = ''
                            logger.info("{0} plot is on cache".format(order.orderid))
                        p.save()
        return True

    def handle_submitted_products(self):
        """
        Handles all submitted products in the system
        :return: True
        """
        logger.info('Handling submitted products...')
        self.handle_submitted_landsat_products()
        self.handle_submitted_modis_products()
        self.handle_submitted_plot_products()
        return True

    def send_completion_email(self, order):
        """
        Public interface to send the completion email
        :param order: order id
        :return: True
        """
        return emails.Emails().send_completion(order)

    def update_order_if_complete(self, order_id):
        """
        Method to send out the order completion email
        for orders if the completion of a scene
        completes the order
        :param order_id: the order id
        :return: True
        """
        order = order_id if isinstance(order_id, Order) else Order.find(order_id)

        if not type(order) == Order:
            msg = "%s must be of type Order, int or str" % order
            raise TypeError(msg)

        # find all scenes that are not complete
        scenes = order.scenes({'status NOT ': ('complete', 'unavailable')})
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
                        logger.debug('Completion email not sent for {0}'.format(order.orderid))
                        raise ProductionProviderException("Completion email not sent from "
                                                          "update_order_if_complete\nfor order {}".format(order.orderid))
                    else:
                        order.completion_email_sent = datetime.datetime.now()
                        order.save()
                except Exception, e:
                    logger.debug('Error calling send_completion_email\nexception: {}'.format(e))
                    raise e
        return True

    def finalize_orders(self):
        """
        Checks all open orders in the system and marks them complete if all
        required scene processing is done
        :return: True
        """
        orders = Order.where({'status': 'ordered'})
        [self.update_order_if_complete(o) for o in orders]
        return True

    def purge_orders(self, send_email=False):
        """
        Will move any orders older than X days to purged status and will also
        remove the files from disk
        :param send_email: boolean
        :return: True
        """
        days = config.get('policy.purge_orders_after')
        cutoff = datetime.datetime.now() - datetime.timedelta(days=int(days))
        orders = Order.where({'status': 'complete', 'completion_date <': cutoff})
        start_capacity = onlinecache.capacity()

        logger.info('Using purge policy of {0} days'.format(days))
        logger.info('Purging {0} orders from the active record.'.format(len(orders)))
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
            except Exception as e:
                logger.debug('Exception purging {0}\nexception: {1}'.format(order.orderid, e))

        end_capacity = onlinecache.capacity()
        logger.info('Ending cache capacity:{0}'.format(end_capacity))

        if send_email is True:
            logger.info('Sending purge report')
            emails.send_purge_report(start_capacity, end_capacity, orders)

        return True

    @staticmethod
    def handle_failed_ee_updates():
        scenes = Scene.where({'failed_lta_status_update IS NOT': None})
        for s in scenes:
            try:
                lta.update_order_status(s.order_attr('ee_order_id'), s.ee_unit_id,
                                        s.failed_lta_status_update)
                s.update('failed_lta_status_update', None)
            except DBConnectException, e:
                raise ProductionProviderException('ordering_scene update failed for '
                                                  'handle_failed_ee_updates: {}'.format(e))
            except Exception, e:
                # LTA could still be unavailable, log and it'll be tried again later
                logger.warn('Failed EE update retry failed again for '
                            'scene {}\n{}'.format(s.id, e))
        return True

    def handle_orders(self):
        """
        Logic handler for how we accept orders + products into the system
        :return: True
        """
        self.send_initial_emails()
        self.handle_onorder_landsat_products()
        self.handle_retry_products()
        self.load_ee_orders()
        self.handle_failed_ee_updates()
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

    @staticmethod
    def strip_unrelated(sceneid, opts):
        """
        Remove unnecessary keys from options
        :param sceneid: scene name
        :param opts: processing options
        :return: dict
        """
        opts = copy.deepcopy(opts)
        short = sensor.instance(sceneid).shortname
        sen_keys = sensor.SensorCONST.instances.keys()
        opts['products'] = opts[short]['products']

        for sen in sen_keys:
            if sen in opts:
                opts.pop(sen)

        return opts

    @staticmethod
    def production_whitelist():
        cache_key = 'prod_whitelist'
        prodlist = cache.get(cache_key)
        if prodlist is None:
            logger.info("Regenerating production whitelist...")
            # timeout in 6 hours
            timeout = 60 * 60 * 6
            prodlist = list(['127.0.0.1', socket.gethostbyname(socket.gethostname())])
            prodlist.append(hadoop_handler.master_ip())
            prodlist.extend(hadoop_handler.slave_ips())
            cache.set(cache_key, prodlist, timeout)

        return prodlist

    @staticmethod
    def catch_orphaned_scenes():
        o_time = datetime.datetime.now()

        def find_orphans():
            job_dict = hadoop_handler.job_names_ids()
            queued_scenes = Scene.where({'status': ('queued', 'processing')})
            return [scene for scene in queued_scenes if scene.job_name not in job_dict]

        for scene in find_orphans():
            if not scene.orphaned:
                # scenes already marked orphaned can be ignored here
                if scene.reported_orphan:
                    # has enough time lapsed to confidently mark it orphaned?
                    d_time = o_time - scene.reported_orphan
                    if (d_time.seconds / 60) > 10:
                        scene.orphaned = True
                else:
                    # the scenes been newly reported an orphan, note the time
                    scene.reported_orphan = o_time

                scene.save()

        return True

