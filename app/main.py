from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from jose import jwt, exceptions
from pprint import pprint
import sys

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
item_put_args.add_argument("name", type=str, help="Name des Artikels "+
                              "ist benötigt!", required=True)
item_put_args.add_argument("price", type=float, help="Preis des Artikels "+
                              "ist benötigt!", required=True)

item_update_args = reqparse.RequestParser()
item_update_args.add_argument("price", type=float, help="Preis des Artikels "+
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
            abort(409,  message="Artikel_id exestiert bereits!")
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
            abort(404,  message="Artikel nicht gefunden!")
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
        return '',204
    
    
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

if __name__ == "__main__":
    app.run(debug=True)