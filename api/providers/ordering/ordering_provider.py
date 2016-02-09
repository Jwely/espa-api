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
            db.select(sql, (ordernum))
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
            db.select(sql, orderid)
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
            argtup = (orderid)
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

