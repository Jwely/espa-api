from api.util.dbconnect import DBConnect, DBConnectException
from api.domain.order import OptionsMappings
from api.util import api_cfg


class ConvertProductOptions(object):
    """
    Convert the old product_options column into the new
    product_opts jsonb column type and order structure

    Ideally this should only need to be run once, during the
    change over
    """
    db = DBConnect(**api_cfg())

    def convert(self):
        current_orders = self._retrieve_orders()

        for co in current_orders:
            # Already exists
            if co['product_opts']:
                continue

            scenes = self._retrieve_scenes(co['id'])
            prod_opts = OptionsMappings.convert(old=co['product_options'], scenes=scenes)
            self._update_product_opts(prod_opts, co['id'])

    def _retrieve_orders(self):
        sql = ('select id, product_options, product_opts '
               'from ordering_order')

        self.db.select(sql)
        ret = [r for r in self.db]

        return ret

    def _retrieve_scenes(self, oid):
        sql = ('select name, completion_date '
               'from ordering_scene '
               'where order_id = %s')

        self.db.select(sql, (oid,))
        ret = [r for r in self.db]

        return ret

    def _update_product_opts(self, opts, oid):
        sql = ('update ordering_order '
               'set product_opts = %s '
               'where id = %s')

        try:
            self.db.execute(sql, (opts, oid))
            self.db.commit()
        except DBConnectException:
            self.db.rollback()
            raise

    def __del__(self):
        self.db.__del__()
