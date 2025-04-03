from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)

class ItemModel(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)
    store = db.relationship("StoreModel", back_populates="items")

class StoreModel(db.Model):
    __tablename__ = "stores"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic")

class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)

item_schema = ItemSchema()
store_schema = StoreSchema()
items_schema = ItemSchema(many=True)

class Item(Resource):
    def get(self, name):
        item = ItemModel.query.filter_by(name=name).first()
        if item:
            return item_schema.dump(item)
        return {"message": "Item not found"}, 404

    def post(self):
        data = request.get_json()
        item = ItemModel(**data)
        db.session.add(item)
        db.session.commit()
        return item_schema.dump(item)

    def delete(self, name):
        item = ItemModel.query.filter_by(name=name).first()
        if item:
            db.session.delete(item)
            db.session.commit()
        return {"message": "Item deleted"}

class Store(Resource):
    def post(self):
        data = request.get_json()
        store = StoreModel(**data)
        db.session.add(store)
        db.session.commit()
        return store_schema.dump(store)

    def get(self, name):
        store = StoreModel.query.filter_by(name=name).first()
        if store:
            return store_schema.dump(store)
        return {"message": "Store not found"}, 404

api.add_resource(Item, "/item/<string:name>", "/item")
api.add_resource(Store, "/store/<string:name>", "/store")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
