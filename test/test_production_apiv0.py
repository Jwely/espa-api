#!/usr/bin/env python
import datetime
import unittest

import os
from api.domain.mocks.order import MockOrder
from api.domain.mocks.user import MockUser
from api.domain.order import Order
from api.domain.scene import Scene
from api.domain.user import User
from api.external.mocks import lta, lpdaac, onlinecache, nlaps
from api.interfaces.production.version0 import API
from api.notification import emails
from api.providers.production.mocks.production_provider import MockProductionProvider
from api.providers.production.production_provider import ProductionProvider
from api.system.mocks import errors
from mock import patch

api = API()
production_provider = ProductionProvider()
mock_production_provider = MockProductionProvider()

class TestProductionAPI(unittest.TestCase):
    def setUp(self):
        os.environ['espa_api_testing'] = 'True'
        # create a user
        self.mock_user = MockUser()
        self.mock_order = MockOrder()
        self.user_id = self.mock_user.add_testing_user()

    def tearDown(self):
        # clean up orders
        self.mock_order.tear_down_testing_orders()
        # clean up users
        self.mock_user.cleanup()
        os.environ['espa_api_testing'] = ''

    @patch('api.external.lpdaac.get_download_urls', lpdaac.get_download_urls)
    @patch('api.providers.production.production_provider.ProductionProvider.set_product_retry',
           mock_production_provider.set_product_retry)
    def test_fetch_production_products_modis(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        # need scenes with statuses of 'processing' and 'ordered'
        self.mock_order.update_scenes(order_id, 'status', ['processing', 'ordered', 'oncache'])
        user = User.where("id = {0}".format(self.user_id))[0]
        params = {'for_user': user.username, 'product_types': ['modis']}
        response = api.fetch_production_products(params)
        self.assertTrue('bilbo' in response[0]['orderid'])

    @patch('api.external.lta.get_download_urls', lta.get_download_urls)
    @patch('api.providers.production.production_provider.ProductionProvider.set_product_retry',
           mock_production_provider.set_product_retry)
    def test_fetch_production_products_landsat(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        # need scenes with statuses of 'processing' and 'ordered'
        self.mock_order.update_scenes(order_id, 'status', ['processing','ordered','oncache'])
        user = User.where("id = {0}".format(self.user_id))[0]
        params = {'for_user': user.username, 'product_types': ['landsat']}
        response = api.fetch_production_products(params)
        self.assertTrue('bilbo' in response[0]['orderid'])

    def test_fetch_production_products_plot(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        self.mock_order.update_scenes(order_id, 'status', ['complete'])
        order = Order.where({'id': order_id})[0]
        plot_scene = order.scenes()[0]
        plot_scene.name = 'plot'
        plot_scene.sensor_type = 'plot'
        plot_scene.status = 'submitted'
        plot_scene.save()
        response = production_provider.handle_submitted_plot_products()
        pscene = order.scenes({'status': 'oncache', 'sensor_type': 'plot'})
        self.assertTrue(response is True)
        self.assertEqual(len(pscene), 1)

    def test_production_set_product_retry(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        scene = order.scenes()[3]
        scene.update('retry_count', 4)
        processing_loc = "get_products_to_process"
        error = 'not available after EE call '
        note = 'note this'
        retry_after = datetime.datetime.now() + datetime.timedelta(hours=1)
        retry_limit = 9
        response = production_provider.set_product_retry(scene.name, order.orderid, processing_loc,
                                                         error, note, retry_after, retry_limit)

        new = Scene.get('ordering_scene.status', scene.name, order.orderid)
        self.assertTrue('retry' == new)

    @patch('api.external.lta.update_order_status', mock_production_provider.respond_true)
    # @patch('api.system.errors.resolve', errors.resolve_unavailable)
    def test_production_set_product_error_unavailable(self):
        """
        Move a scene status from error to unavailable based on the error
        message
        """
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]

        for s in order.scenes():
            if s.name != 'plot':
                scene = s
                break

        processing_loc = "get_products_to_process"
        error = 'include_dswe is an unavailable product option for OLITIRS'
        response = production_provider.set_product_error(scene.name, order.orderid,
                                                         processing_loc, error)

        new = Scene.get('ordering_scene.status', scene.name, order.orderid)
        self.assertTrue('unavailable' == new)

    def test_production_set_product_error_submitted(self):
        """
        Move a scene status from error to submitted based on the error
        message
        """
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]

        for s in order.scenes():
            if s.name != 'plot':
                scene = s
                break

        processing_loc = "get_products_to_process"
        error = 'BLOCK, COMING FROM LST AS WELL: No such file or directory'
        response = production_provider.set_product_error(scene.name,
                                                         order.orderid,
                                                         processing_loc,
                                                         error)

        new = Scene.get('ordering_scene.status', scene.name, order.orderid)
        self.assertTrue('submitted' == new)

    # @patch('api.providers.production.production_provider.ProductionProvider.set_product_retry',
    #        mock_production_provider.set_product_retry)
    # @patch('api.system.errors.resolve', errors.resolve_retry)
    def test_production_set_product_error_retry(self):
        """
        Move a scene status from error to retry based on the error
        message
        """
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]

        scene = order.scenes()[2]

        processing_loc = 'somewhere'
        error = 'Verify the missing auxillary data products'
        response = production_provider.set_product_error(scene.name,
                                                         order.orderid,
                                                         processing_loc,
                                                         error)

        new = Scene.get('ordering_scene.status', scene.name, order.orderid)
        self.assertTrue('retry' == new)

    @patch('api.external.lta.update_order_status', lta.update_order_status)
    @patch('api.providers.production.production_provider.ProductionProvider.set_product_retry', mock_production_provider.set_product_retry)
    def test_update_product_details_update_status(self):
        """
        Set a scene status to Queued
        """
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        scene = order.scenes()[0]
        processing_loc = 'L8SRLEXAMPLE'
        status = 'Queued'
        response = api.update_product_details('update_status',
                                              {'name': scene.name,
                                               'orderid': order.orderid,
                                               'processing_loc': processing_loc,
                                               'status': status})

        new = Scene.get('ordering_scene.status', scene.name, order.orderid)
        self.assertTrue(new == status)

    @patch('api.external.lta.update_order_status', lta.update_order_status)
    @patch('api.providers.production.production_provider.ProductionProvider.set_product_retry', mock_production_provider.set_product_retry)
    # @patch('api.external.onlinecache.capacity', onlinecache.capacity)
    def test_update_product_details_set_product_error(self):
        """
        Set a scene status to error
        :return:
        """
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        scene = order.scenes()[0]
        processing_loc = "L8SRLEXAMPLE"
        error = 'GDAL Warp failed to transform'
        response = production_provider.update_product('set_product_error',
                                                      name=scene.name, orderid=order.orderid,
                                                      processing_loc=processing_loc, error=error)

        new = Scene.get('ordering_scene.status', scene.name, order.orderid)
        self.assertTrue('error' == new)

    @patch('api.external.lta.update_order_status', lta.update_order_status)
    @patch('api.providers.production.production_provider.ProductionProvider.set_product_retry', mock_production_provider.set_product_retry)
    def test_update_product_details_set_product_unavailable(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        scene = order.scenes()[0]
        processing_loc = "L8SRLEXAMPLE"
        error = 'include_dswe is an unavailable product option for OLITIRS'
        response = production_provider.update_product('set_product_unavailable',
                                                      name=scene.name, orderid=order.orderid,
                                                      processing_loc=processing_loc, error=error)

        new = Scene.get('ordering_scene.status', scene.name, order.orderid)
        self.assertTrue('unavailable' == new)

    @patch('api.external.lta.update_order_status', lta.update_order_status)
    @patch('api.providers.production.production_provider.ProductionProvider.set_product_retry', mock_production_provider.set_product_retry)
    def test_update_product_details_mark_product_complete(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        scene = order.scenes()[0]
        processing_loc = 'L8SRLEXAMPLE'
        file_loc = '/some/loc'
        cksum = 'some checksum'
        logfile = 'some log'
        response = production_provider.update_product('mark_product_complete',
                                                      name=scene.name,
                                                      orderid=order.orderid,
                                                      processing_loc=processing_loc,
                                                      completed_file_location=file_loc,
                                                      cksum_file_location=cksum,
                                                      log_file_contents=logfile)

        new = Scene.get('ordering_scene.status', scene.name, order.orderid)

        self.assertTrue('complete' == new)

    @patch('api.providers.production.production_provider.ProductionProvider.send_initial_emails',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.handle_onorder_landsat_products',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.handle_retry_products',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.load_ee_orders',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.handle_submitted_products',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.finalize_orders',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.purge_orders',
           mock_production_provider.respond_true)
    def test_handle_orders_success(self):
        response = api.handle_orders()
        self.assertTrue(response)

    @patch('api.external.onlinecache.delete',
           mock_production_provider.respond_true)
    @patch('api.notification.emails.send_purge_report',
           mock_production_provider.respond_true)
    @patch('api.external.onlinecache.capacity',
           onlinecache.capacity)
    def test_production_purge_orders(self):
        new_completion_date = datetime.datetime.now() - datetime.timedelta(days=12)
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        order.update('status', 'complete')
        order.update('completion_date', new_completion_date)
        response = production_provider.purge_orders()
        self.assertTrue(response)

    # need to figure a test for emails.send_email
    @patch('api.notification.emails.Emails.send_email',
           mock_production_provider.respond_true)
    def test_production_send_initial_emails(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        order.update('status', 'ordered')
        response = emails.Emails().send_all_initial()
        self.assertTrue(response)

    @patch('api.external.lta.get_order_status', lta.get_order_status)
    @patch('api.external.lta.update_order_status', lta.update_order_status)
    def test_production_handle_onorder_landsat_products(self):
        tram_order_ids = lta.sample_tram_order_ids()[0:3]
        scene_names = lta.sample_scene_names()[0:3]
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        scenes = order.scenes()[0:3]
        for idx, scene in enumerate(scenes):
            scene.tram_order_id = tram_order_ids[idx]
            scene.status = 'onorder'
            # save() doesn't let you update name,
            # b/c updating a scene name is not acceptable
            # outside of testing
            scene.update('name', scene_names[idx])
            scene.save()

        response = production_provider.handle_onorder_landsat_products()

        self.assertTrue(response)

    def test_production_handle_retry_products(self):
        prev = datetime.datetime.now() - datetime.timedelta(hours=1)
        order_id = self.mock_order.generate_testing_order(self.user_id)
        self.mock_order.update_scenes(order_id, 'status', ['retry'])
        self.mock_order.update_scenes(order_id, 'retry_after', [prev])

        production_provider.handle_retry_products()

        scenes = Scene.where({'order_id': order_id})
        for s in scenes:
            self.assertTrue(s.status == 'submitted')

    @patch('api.external.lta.get_available_orders', lta.get_available_orders)
    @patch('api.external.lta.update_order_status', lta.update_order_status)
    @patch('api.external.lta.get_user_name', lta.get_user_name)
    def test_production_load_ee_orders(self):
        production_provider.load_ee_orders()

    @patch('api.providers.production.production_provider.ProductionProvider.handle_submitted_landsat_products',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.handle_submitted_modis_products',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.handle_submitted_plot_products',
           mock_production_provider.respond_true)
    def test_production_handle_submitted_products(self):
        response = production_provider.handle_submitted_products()
        self.assertTrue(response)

    @patch('api.providers.production.production_provider.ProductionProvider.mark_nlaps_unavailable',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.update_landsat_product_status',
           mock_production_provider.respond_true)
    @patch('api.providers.production.production_provider.ProductionProvider.get_contactids_for_submitted_landsat_products',
           mock_production_provider.contact_ids_list)
    def test_production_handle_submitted_landsat_products(self):
        response = production_provider.handle_submitted_landsat_products()
        self.assertTrue(response)

    # !!! need to write test for nlaps.products_are_nlaps !!!
    @patch('api.external.nlaps.products_are_nlaps', nlaps.products_are_nlaps)
    @patch('api.providers.production.production_provider.ProductionProvider.set_products_unavailable',
           mock_production_provider.respond_true)
    def test_production_mark_nlaps_unavailable(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        scenes = Order.where({'id': order_id})[0].scenes()
        for scene in scenes:
            scene.status = 'submitted'
            scene.sensor_type = 'landsat'
            scene.save()
        response = production_provider.mark_nlaps_unavailable()
        self.assertTrue(response)

    @patch('api.external.lta.update_order_status', lta.update_order_status)
    def test_production_set_products_unavailable(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        scenes = Order.where({'id': order_id})[0].scenes()
        response = production_provider.set_products_unavailable(scenes, "you want a reason?")
        self.assertTrue(response)

    @patch('api.external.lta.order_scenes', lta.order_scenes)
    @patch('api.providers.production.production_provider.ProductionProvider.set_products_unavailable',
           mock_production_provider.respond_true)
    def test_production_update_landsat_product_status(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        scenes = Order.where({'id': order_id})[0].scenes()
        for scene in scenes:
            scene.status = 'submitted'
            scene.sensor_type = 'landsat'
            scene.save()
        user = User.where("id = {0}".format(self.user_id))[0]
        response = production_provider.update_landsat_product_status(user.contactid)
        self.assertTrue(response)

    def test_production_get_contactids_for_submitted_landsat_products(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        scenes = Order.where({'id': order_id})[0].scenes()
        for scene in scenes:
            scene.status = 'submitted'
            scene.sensor_type = 'landsat'
            scene.save()
        response = production_provider.get_contactids_for_submitted_landsat_products()
        self.assertIsInstance(response, set)
        self.assertTrue(len(response) > 0)

    @patch('api.external.lpdaac.input_exists', lpdaac.input_exists_true)
    def test_production_handle_submitted_modis_products_input_exists(self):
        # handle oncache scenario
        order_id = self.mock_order.generate_testing_order(self.user_id)
        scenes = Order.where({'id': order_id})[0].scenes()
        for scene in scenes:
            scene.status = 'submitted'
            scene.sensor_type = 'modis'
            scene.save()
        response = production_provider.handle_submitted_modis_products()
        scene = Scene.where({'id': scenes[0].id})[0]
        self.assertTrue(response)
        self.assertEquals(scene.status, "oncache")

    @patch('api.external.lpdaac.input_exists', lpdaac.input_exists_false)
    def test_production_handle_submitted_modis_products_input_missing(self):
        # handle unavailable scenario
        order_id = self.mock_order.generate_testing_order(self.user_id)
        scenes = Order.where({'id': order_id})[0].scenes()
        for scene in scenes:
            scene.status = 'submitted'
            scene.sensor_type = 'modis'
            scene.save()
        response = production_provider.handle_submitted_modis_products()
        scene = Scene.where({'id': scenes[0].id})[0]
        self.assertTrue(response)
        self.assertEquals(scene.status, "unavailable")

    def test_production_handle_submitted_plot_products(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        order.status = 'ordered'
        order.order_type = 'lpcs'
        order.save()
        plot_id = None
        for idx, scene in enumerate(order.scenes()):
            # at the moment, mock_order.generate_testing_order
            # creates 21 products for the order. divvy those
            # up between 'complete' and 'unavailable', setting
            # one aside as the 'plot' product
            if idx % 2 == 0:
                if idx == 0:
                    # need to define a plot product
                    scene.update('status', 'submitted')
                    scene.update('sensor_type', 'plot')
                    plot_id = scene.id
                else:
                    scene.update('status', 'complete')
            else:
                scene.update('status', 'unavailable')

        response = production_provider.handle_submitted_plot_products()

        plot_product = Scene.where({'id': plot_id})[0]
        self.assertEqual(plot_product.status, "oncache")
        self.assertTrue(response)

    @patch('api.providers.production.production_provider.ProductionProvider.update_order_if_complete',
           mock_production_provider.respond_true)
    def test_production_finalize_orders(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        order.update('status', 'ordered')
        response = production_provider.finalize_orders()
        self.assertTrue(response)

    @patch('api.providers.production.production_provider.ProductionProvider.send_completion_email',
           mock_production_provider.respond_true)
    def test_production_update_order_if_complete(self):
        order_id = self.mock_order.generate_testing_order(self.user_id)
        order = Order.where({'id': order_id})[0]
        scenes = order.scenes()
        Scene.bulk_update([s.id for s in scenes], {'status': 'retry'})
        order.order_source = 'espa'
        order.completion_email_sent = None
        order.save()
        response = production_provider.update_order_if_complete(order)
        self.assertTrue(response)

    def test_production_queue_products_success(self):
        names_tuple = self.mock_order.names_tuple(3, self.user_id)
        processing_loc = "get_products_to_process"
        job_name = 'jobname49'
        params = (names_tuple, processing_loc, job_name)
        response = api.queue_products(*params)
        self.assertTrue(response)

    def test_production_get_key(self):
        key = 'system_message_title'
        response = api.get_production_key(key)
        val = response[key]
        self.assertIsInstance(val, str)

    def test_get_production_key_invalid(self):
        bad_key = 'foobar'
        response = api.get_production_key(bad_key)
        self.assertEqual(response.keys(), ['msg'])



if __name__ == '__main__':
    unittest.main(verbosity=2)
