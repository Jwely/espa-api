from api.util.dbconnect import DBConnect, DBConnectException
from api.domain import sensor
from api.domain.order import Order
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

    def _build_opts(self):
        pass

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

    def _update_productopts(self, opts, oid):
        sql = ('update ordering_order '
               'set product_opts = %s '
               'where id = %s')

        try:
            self.db.execute(sql, (opts, oid))
            self.db.commit()
        except DBConnectException:
            self.db.rollback()
            raise
