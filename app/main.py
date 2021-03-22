from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from jose import jwt, exceptions

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class ItemModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Item(itemId = {id}, name = {self.name}, price= {self.price})"


item_put_args = reqparse.RequestParser()
item_put_args.add_argument("name", type=str, help="Name des Artikels " +
                                                  "ist benötigt!", required=True)
item_put_args.add_argument("price", type=float, help="Preis des Artikels " +
                                                     "ist benötigt!", required=True)

item_update_args = reqparse.RequestParser()
item_update_args.add_argument("price", type=float, help="Preis des Artikels " +
                                                        "ist benötigt!", required=True)

reource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'price': fields.Float
}

key = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"


def user_vali(token):
    try:
        payload = jwt.decode(token, key, algorithms=['HS256'])
        role = payload['role']
        return role
    except exceptions.JWTError:
        return None


class Item(Resource):
    @marshal_with(reource_fields)
    def get(self, itemId):
        role = user_vali(request.headers.get('Authorization')[7:])
        if not role:
            abort(429, message="Ungültiger benutzer!")
        if role != 'manager' and role != 'user':
            abort(429, message="Ungültiger benutzer!")

        result = ItemModel.query.filter_by(id=itemId).first()
        if not result:
            abort(404, message="Artikel nicht gefunden!")

        return result

    @marshal_with(reource_fields)
    def put(self, itemId):
        args = item_put_args.parse_args()

        role = user_vali(request.headers.get('Authorization')[7:])
        if not role:
            abort(429, message="Ungültiger benutzer!")
        if role != 'manager':
            abort(429, message="Ungültiger benutzer!")

        result = ItemModel.query.filter_by(id=itemId).first()
        if result:
            abort(409, message="Artikel_id exestiert bereits!")
        item = ItemModel(id=itemId, name=args['name'], price=args['price'])
        db.session.add(item)
        db.session.commit()
        return item, 201

    @marshal_with(reource_fields)
    def patch(self, itemId):
        args = item_update_args.parse_args()

        role = user_vali(request.headers.get('Authorization')[7:])
        if not role:
            abort(429, message="Ungültiger benutzer!")
        if role != 'manager':
            abort(429, message="Ungültiger benutzer!")

        result = ItemModel.query.filter_by(id=itemId).first()
        if not result:
            abort(404, message="Artikel nicht gefunden!")
        result.price = args['price']
        db.session.commit()
        return result

    def delete(self, itemId):

        role = user_vali(request.headers.get('Authorization')[7:])
        if not role:
            abort(429, message="Ungültiger benutzer!")
        if role != 'manager':
            abort(429, message="Ungültiger benutzer!")

        result = ItemModel.query.filter_by(id=itemId).first()
        if not result:
            abort(404, message="Artikel nicht gefunden!")
        db.session.remove(result)
        db.session.commit()
        return '', 204


api.add_resource(Item, "/item/<int:itemId>")


class Items(Resource):
    @marshal_with(reource_fields)
    def get(self):
        role = user_vali(request.headers.get('Authorization')[7:])
        if not role:
            abort(429, message="Ungültiger benutzer!")
        if role != 'manager' and role != 'user':
            abort(429, message="Ungültiger benutzer!")

        items = ItemModel.query.all()
        return items, 200


api.add_resource(Items, "/item/all")


def register_with_registry():
    """Register with consul service registry if available and running.
    """
    import os
    import sys
    import consulate
    from requests.exceptions import ConnectionError

    # Get connection information of discovery service
    DISCOVERY_ADDRESS = os.environ.get("DISCOVERY_ADDRESS") or "localhost"
    DISCOVERY_PORT = os.environ.get("DISCOVERY_PORT") or 8500
    DISCOVERY_SCHEME = os.environ.get("DISCOVERY_SCHEME") or "http"

    # Port of this service. Recquired for registering with consul discovery service.
    SERVICE_PORT = os.environ.get("SERVICE_PORT") or 5100

    local_ip = None

    SERVICE_ADDRESS = local_ip or "localhost"

    try:
        consul = consulate.Consul(host=DISCOVERY_ADDRESS, port=DISCOVERY_PORT, scheme=DISCOVERY_SCHEME)

        # Add a service to the local agent
        consul.agent.service.register('users',
                                      port=SERVICE_PORT,
                                      address=SERVICE_ADDRESS)
        print("[INFO] Registered with Service Registry!")
    except ConnectionError:
        print(
            "[ConnectionError] Could not register to consul discovery service.. Maybe discovery service is not running.",
            file=sys.stderr)


if __name__ == "__main__":
    try:
        register_with_registry()
    except ImportError as err:
        print("[Error] Missing consul client library. Check if consulate is installed in your environment.")

    app.run(debug=False)
