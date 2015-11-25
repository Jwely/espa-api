import jsonify
import api
import converters

from flask import Blueprint

ordering = Blueprint('ordering', __name__)
converters.url_map.converters['regex'] = api.RegexConverter

#@ordering.route('/list', methods=['GET'])
#@ordering.route('/list/<email>', methods=['GET'])

@ordering.route('/', methods=['GET'])
@ordering.route('/<regex("[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}"):email>',
                 methods=['GET'])
@api.requires_auth
def list_orders(email=None):
    orders = None
    if email is None:
        user = request.authorization.username
    else:
        try:
            user = db.username(email)
            orders = db.list_orders(user)
        except:
            pass
    return jsonify(orders=orders)


@ordering.route('/', methods=['POST'])
@api.requires_auth
def place_order():
    user = request.authorization.username
    order = request.get_json(force=True)
    v = schema.OrderValidator(schema.order_schema)
    if v.validate(order) == False:
        return jsonify(errors=v.errors)
    else:
        return jsonify(db.save_order(user, order))


@ordering.route('/<regex("[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}-[0-9]{13}"):ordernum>',
                methods=['GET'])
@ordering.route('/<regex("[A-Za-z0-9._%+-\\\']+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}.*"):ordernum>',
                methods=['GET'])
#@ordering.route('/view/<ordernum>', methods=['GET'])
@api.requires_auth
def order_details(ordernum):
    return jsonify(db.view_order(ordernum))
