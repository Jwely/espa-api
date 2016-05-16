import os
import json
import pprint

from api.util.dbconnect import db_instance, DBConnectException, DBConnect
from api.domain.order import OptionsConversion
from api.util import api_cfg


class ConvertProductOptions(object):
    """
    Convert the old product_options column into the new
    product_opts jsonb column type and order structure

    Ideally this should only need to be run once, during the
    change over
    """
    # cfg = os.path.join(os.path.expanduser('~/.usgs'), '.cfgnfo_dupe')
    # print api_cfg(section='db', cfgfile=cfg)
    # db = DBConnect(**api_cfg(section='db', cfgfile=cfg))
    db = db_instance()

    def convert(self):
        current_orders = self._retrieve_orders()

        for co in current_orders:
            if not co['product_options']:
                co['product_options'] = '{"include_sr": true}'

            scenes = self._retrieve_scenes(co['id'])

            if not scenes:
                continue

            try:
                prod_opts = OptionsConversion.convert(old=json.loads(co['product_options']), scenes=scenes)
            except:
                raise

            self._update_product_opts(json.dumps(prod_opts), co['id'])

        try:
            self.db.commit()
        except:
            raise

    def _retrieve_orders(self):
        sql = ('select id, product_options, product_opts '
               'from ordering_order')

        self.db.select(sql)

        return [r for r in self.db]

    def _retrieve_scenes(self, oid):
        sql = ('select name '
               'from ordering_scene '
               'where order_id = %s')

        self.db.select(sql, (oid,))

        return [r['name'] for r in self.db]

    def _update_product_opts(self, opts, oid):
        sql = ('update ordering_order '
               'set product_opts = %s '
               'where id = %s')

        try:
            self.db.execute(sql, (opts, oid))
        except DBConnectException:
            raise

    def __del__(self):
        self.db.__del__()
