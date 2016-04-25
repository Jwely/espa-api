import datetime

from api.domain import sensor
from api.domain.order import Order
from api.util.dbconnect import db_instance, DBConnectException
from validate_email import validate_email
from api.providers.ordering import ProviderInterfaceV0
from api.providers.configuration.configuration_provider import ConfigurationProvider

import yaml
import copy
import memcache

cache = memcache.Client(['127.0.0.1:11211'], debug=0)


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
        with db_instance() as db:
            # username uniqueness enforced on auth_user table at database
            user_sql = "select id, username, email, is_staff, is_active, " \
                       "is_superuser from auth_user where username = %s;"
            db.select(user_sql, (username))

        return db[0]

    def available_products(self, product_id, username):
        userlist = OrderingProvider.fetch_user(username)
        pub_prods = copy.deepcopy(OrderingProvider.sensor_products(product_id))

        if not userlist['is_staff']:
            with open('api/domain/restricted.yaml') as f:
                restricted = yaml.load(f.read())

            for sensor_type in pub_prods:
                sensor_restr = restricted.get(sensor_type, [])
                sensor_restr.extend(restricted.get('all'))

                if sensor_type == 'not_implemented':
                    continue
                for restr in sensor_restr:
                    if restr in pub_prods[sensor_type]['outputs']:
                        pub_prods[sensor_type]['outputs'].remove(restr)

        return pub_prods

    def fetch_user_orders(self, uid, filters={}):
        # deal with unicode uid
        if isinstance(uid, basestring):
            uid = str(uid)
        id_type = 'email' if validate_email(uid) else 'username'
        order_list = []
        out_dict = {}

        with db_instance() as db:
            user_sql = "select id, username, email from auth_user where "
            user_sql += "email = %s;" if id_type == 'email' else "username = %s;"

            db.select(user_sql, (uid))
            # username uniqueness enforced on the db
            # not the case for emails though
            if db:
                user_ids = [db[ind][0] for ind, val in enumerate(db)]
            else:
                return {"msg": "sorry, no user matched {0}".format(uid)}

            if user_ids:
                user_tup = tuple([str(idv) for idv in user_ids])

                sql = "select orderid from ordering_order where user_id in %(user_tup)s"
                params = {'user_tup': user_tup}

                if filters:
                    for key, val in filters.iteritems():
                        if isinstance(val, list):
                            val = tuple([v for v in val])
                            op = " IN "
                        else:
                            op = " = "

                        params[key] = val
                        sql += " AND {0} {1} %({0})s ".format(key, op)

                db.select(sql, params)

                if db:
                    order_list = [item[0] for item in db]

        out_dict["orders"] = order_list
        return out_dict

    def fetch_user_orders_ext(self, uid, filters={}):
        orders = self.fetch_user_orders(uid, filters=filters)
        if 'orders' not in orders.keys():
            return orders
        orders_d = orders['orders']
        output = []
        for orderid in orders_d:
            order = Order.where("orderid = '{0}'".format(orderid))[0]
            products_ordered = len(order.scenes())
            products_complete = len(order.scenes(["status = 'complete'"]))
            out_d = {'orderid': orderid, 'products_ordered': products_ordered,
                     'products_complete': products_complete,
                     'order_status': order.status, 'order_note': order.note}
            output.append(out_d)
        return output

    def fetch_user_orders_feed(self, email):
        orders = self.fetch_user_orders(email)
        if 'orders' not in orders.keys():
            return orders

        outd = {}
        for orderid in orders['orders']:
            order = Order.where("orderid = '{0}'".format(orderid))[0]
            scenes = order.scenes(["status = 'complete'"])
            if scenes:
                outd[order.orderid] = {'orderdate': str(order.order_date)}
                scene_list = []
                for scene in scenes:
                    scene_list.append({'name': scene.name,
                                       'url': scene.product_dload_url,
                                       'status': scene.status})
                outd[order.orderid]['scenes'] = scene_list

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
        note = new_order.pop('note') if 'note' in new_order.keys() else None
        order_dict = {}
        order_dict['orderid'] = Order.generate_order_id(user.email)
        order_dict['user_id'] = user.id
        order_dict['order_type'] = 'level2_ondemand'
        order_dict['status'] = 'ordered'
        order_dict['product_opts'] = new_order
        order_dict['ee_order_id'] = ''
        order_dict['order_source'] = 'espa'
        order_dict['order_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        order_dict['priority'] = 'normal'
        order_dict['note'] = note
        order_dict['email'] = user.email
        order_dict['product_options'] = ''

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

    def item_status(self, orderid, itemid='ALL'):
        response = {}
        sql = "select oo.orderid, os.name, os.status, os.completion_date, os.note, " \
              "os.product_dload_url, os.cksum_download_url " \
              "from ordering_order oo left join ordering_scene os on oo.id = " \
              "os.order_id where oo.orderid = %s"
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
                ts = ''
                try:
                    # Not always present
                    ts = item['completion_date'].strftime('%m-%d-%Y %H:%M:%S')
                except:
                    pass

                i = {'name': item['name'],
                     'status': item['status'],
                     'completion_date': ts,
                     'note': item['note'],
                     'product_dload_url': item['product_dload_url'],
                     'cksum_download_url': item['cksum_download_url']}
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

    def update_system_status(self, params):

        if params.keys().sort() is not ['system_message_title', 'system_message_body', 'display_system_message'].sort():
            return {'msg': 'Only 3 params are valid, and they must be present: system_message_title, system_message_body, display_system_message'}

        sql_dict = {'msg.system_message_title': params['system_message_title'],
                    'msg.system_message_body': params['system_message_body'],
                    'system.display_system_message': params['display_system_message']}
        sql = ""
        for k, v in sql_dict.iteritems():
            sql += "update ordering_configuration set value = '{0}' where key = '{1}';".format(v, k)

        try:
            with db_instance() as db:
                db.execute(sql)
                db.commit()
        except DBConnectException as e:
            logger.debug("error updating system status: {}".format(e))
            return {'msg': "error updating database: {}".format(e.message)}

        return True

    def get_system_config(self):
        return ConfigurationProvider()._retrieve_config()
