from api.dbconnect import DBConnect
from api.utils import api_cfg

cfg = api_cfg()
cfg['autocommit'] = True
new_column_name = 'product_opts'
old_column_name = 'product_options'


def add_jsonb_order_options():

    with DBConnect(**cfg) as db:

        # add new jsonb field
        db.select("select column_name from information_schema.columns"\
                    " where table_name = 'ordering_order';")
        columns = [db[k][0] for k, v in enumerate(db)]

        if new_column_name not in columns:
            # lets try and add it
            add_col_sql = "ALTER TABLE ordering_order ADD COLUMN %s jsonb;" % new_column_name
            db.execute(add_col_sql)


def migrate_product_options():

    with DBConnect(**cfg) as db:
      sql = "update ordering_order set {0} = {1}::jsonb;".format(new_column_name, old_column_name)
      db.execute(sql)

