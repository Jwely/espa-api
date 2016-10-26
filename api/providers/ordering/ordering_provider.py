import datetime

from api.domain import sensor
from api.domain.order import Order
from api.domain.user import User
from api.util.dbconnect import db_instance
from api.util import julian_date_check
from api.providers.ordering import ProviderInterfaceV0
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.providers.caching.caching_provider import CachingProvider

import copy
import yaml

cache = CachingProvider()
config = ConfigurationProvider()


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

    def available_products(self, product_id, username):
        """
        Check to see what products are available to user based on
        an input list of scenes

        :param product_id: list of desired inputs
        :param username: username
        :return: dictionary
        """
        user = User.by_username(username)
        pub_prods = copy.deepcopy(OrderingProvider.sensor_products(product_id))

        with open('api/domain/restricted.yaml') as f:
                restricted = yaml.load(f.read())

        role = False if user.is_staff() else True

        restrict_all = restricted.get('all', {})
        all_role = restrict_all.get('role', [])
        all_by_date = restrict_all.get('by_date', {})

        upd = {'date_restricted': {}}
        for sensor_type, prods in pub_prods.items():
            if sensor_type == 'not_implemented':
                continue

            sensor_restr = restricted.get(sensor_type, {})
            role_restr = sensor_restr.get('role', []) + all_role
            by_date_restr = sensor_restr.get('by_date', {})

            # All overrides any sensor related dates
            by_date_restr.update(all_by_date)

            outs = pub_prods[sensor_type]['products']
            ins = pub_prods[sensor_type]['inputs']

            remove_me = []
            if role:
                for prod in role_restr:
                    try:
                        outs.remove(prod)
                    except ValueError:
                        continue

            for prod in outs:
                if prod in by_date_restr:
                    r = sensor_restr['by_date'][prod]
                    for sc_id in ins:
                        obj = sensor.instance(sc_id)
                        julian = '{}{}'.format(obj.year, obj.doy)

                        if not julian_date_check(julian, r):
                            remove_me.append(prod)

                            if prod in upd['date_restricted']:
                                upd['date_restricted'][prod].append(sc_id)
                            else:
                                upd['date_restricted'][prod] = [sc_id]

            for rem in remove_me:
                try:
                    outs.remove(rem)
                except ValueError:
                    continue

        if upd['date_restricted']:
            pub_prods.update(upd)

        return pub_prods

    def fetch_user_orders(self, uid, filters=None):
        # deal with unicode uid
        if isinstance(uid, basestring):
            uid = str(uid)

        try:
            user = User.where({'username': uid}).pop()
        except IndexError:
            try:
                user = User.where({'email': uid}).pop()
            except IndexError:
                return {'msg': 'sorry, no user matched {0}'.format(uid)}

        if filters and not isinstance(filters, dict):
            raise OrderingProviderException('filters param must be of type dict')
        elif filters:
            params = dict(filters)
            params.update({'user_id': user.id})
        else:
            params = {'user_id': user.id}

        return {'orders': [o.orderid for o in Order.where(params)]}

    def fetch_user_orders_ext(self, uid, filters={}):
        orders = self.fetch_user_orders(uid, filters=filters)
        if 'orders' not in orders.keys():
            return orders
        orders_d = orders['orders']
        output = []
        for orderid in orders_d:
            order = Order.find(orderid)
            products_complete = order.scene_status_count('complete')
            products_error = order.scene_status_count('error')
            products_ordered = order.scene_status_count()

            out_d = {'orderid': orderid, 'products_ordered': products_ordered,
                     'products_complete': products_complete,
                     'products_error': products_error,
                     'order_status': order.status, 'order_note': order.note}
            output.append(out_d)
        return output

    def fetch_user_orders_feed(self, email):
        orders = self.fetch_user_orders(email)
        if 'orders' not in orders.keys():
            return orders

        cache_key = "{0}_feed".format(email)
        outd = cache.get(cache_key) or {}

        if not outd:
            for orderid in orders['orders']:
                order = Order.find(orderid)
                scenes = order.scenes({"status": "complete"})
                if scenes:
                    outd[order.orderid] = {'orderdate': str(order.order_date)}
                    scene_list = []
                    for scene in scenes:
                        scene_list.append({'name': scene.name,
                                           'url': scene.product_dload_url,
                                           'status': scene.status})
                    outd[order.orderid]['scenes'] = scene_list
            cache.set(cache_key, outd)

        return outd

    def fetch_order(self, ordernum):
        sql = "select * from ordering_order where orderid = %s;"
        out_dict = {}
        opts_dict = {}
        scrub_keys = ['initial_email_sent', 'completion_email_sent', 'id', 'user_id',
                      'ee_order_id', 'email']

        with db_instance() as db:
            db.select(sql, (str(ordernum)))
            if db:
                for key, val in db[0].iteritems():
                    if isinstance(val, datetime.datetime):
                        out_dict[key] = val.isoformat()
                    else:
                        out_dict[key] = val
                opts_str = db[0]['product_options']
                opts_str = opts_str.replace("\n", "")
                opts_dict = yaml.load(opts_str)
                out_dict['product_options'] = opts_dict
            else:
                out_dict['msg'] = "sorry, no order matched that orderid"

        for k in scrub_keys:
            if k in out_dict.keys():
                out_dict.pop(k)

        return out_dict

    def place_order(self, new_order, user):
        """
        Build an order dictionary to be place into the system

        :param new_order: dictionary representation of the order received
        :param user: user information associated with the order
        :return: orderid to be used for tracking
        """
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        order_dict = {'orderid': Order.generate_order_id(user.email),
                      'user_id': user.id,
                      'order_type': 'level2_ondemand',
                      'status': 'ordered',
                      'product_opts': new_order,
                      'ee_order_id': '',
                      'order_source': 'espa',
                      'order_date': ts,
                      'priority': 'normal',
                      'note': new_order.get('note', None),
                      'email': user.email,
                      'product_options': ''}

        result = Order.create(order_dict)
        return result.orderid

    def order_status(self, orderid):
        sql = "select orderid, status from ordering_order where orderid = %s;"
        response = {}
        with db_instance() as db:
            db.select(sql, str(orderid))
            if db:
                for i in ['orderid', 'status']:
                    response[i] = db[0][i]
            else:
                response['msg'] = 'sorry, no orders matched orderid %s' % orderid

        return response

    def item_status(self, orderid, itemid='ALL', username=None):
        response = {}
        sql = "select oo.orderid, os.id scene_id, os.name, os.status, os.completion_date, os.note, " \
              "os.product_dload_url, os.cksum_download_url, os.log_file_contents " \
              "from ordering_order oo left join ordering_scene os on oo.id = " \
              "os.order_id where oo.orderid = %s"
        user = User.by_username(username)

        if itemid is not "ALL":
            argtup = (orderid, itemid)
            sql += " AND os.name = %s;"
        else:
            argtup = (str(orderid))
            sql += ";"

        with db_instance() as db:
            db.select(sql, argtup)
            items = [_ for _ in db.fetcharr]

        if items:
            id = items[0]['orderid']
            response['orderid'] = {id: []}
            for item in items:
                try:
                    ts = item['completion_date'].isoformat()
                except AttributeError:
                    # completion_date not yet set
                    ts = ''

                i = {'scene_id': item['scene_id'],
                     'name': item['name'],
                     'status': item['status'],
                     'completion_date': ts,
                     'note': item['note'],
                     'product_dload_url': item['product_dload_url'],
                     'cksum_download_url': item['cksum_download_url']}

                if user and user.is_staff():
                    i['log_file_contents'] = item['log_file_contents']

                response['orderid'][id].append(i)
        else:
            response['msg'] = 'sorry, no items matched orderid %s , itemid %s' % (orderid, itemid)

        return response

    def get_system_status(self):
        sql = "select key, value from ordering_configuration where " \
              "key in ('msg.system_message_body', 'msg.system_message_title', 'system.display_system_message');"
        with db_instance() as db:
            db.select(sql)

        if db:
            resp_dict = dict(db.fetcharr)
            return {'system_message_body': resp_dict['msg.system_message_body'],
                    'system_message_title': resp_dict['msg.system_message_title'],
                    'display_system_message': resp_dict['system.display_system_message']}
        else:
            return {'system_message_body': None, 'system_message_title': None}
