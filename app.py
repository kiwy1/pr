from flask import Flask, request
from flask_restful import Api, Resource
from db import db
from models import StoreModel, ItemModel
from schemas import ItemSchema, StoreSchema

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)
db.init_app(app)

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
