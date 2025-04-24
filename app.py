from flask import Flask, request
from flask_restful import Api, Resource
from db import db
from models import StoreModel, ItemModel, TagModel
from schemas import ItemSchema, StoreSchema, TagSchema

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)
db.init_app(app)

item_schema = ItemSchema()
store_schema = StoreSchema()
tag_schema = TagSchema()
tags_schema = TagSchema(many=True)

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

class StoreTags(Resource):
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return tags_schema.dump(store.tags.all())

    def post(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        data = request.get_json()
        tag = TagModel(name=data["name"], store_id=store.id)
        db.session.add(tag)
        db.session.commit()
        return tag_schema.dump(tag)

class Tag(Resource):
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag_schema.dump(tag)

    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if tag.items:
            return {"message": "Cannot delete tag with associated items"}, 400
        db.session.delete(tag)
        db.session.commit()
        return {"message": "Tag deleted"}

class LinkTagToItem(Resource):
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        if tag not in item.tags:
            item.tags.append(tag)
            db.session.commit()
        return {"message": "Tag linked to item"}

    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        if tag in item.tags:
            item.tags.remove(tag)
            db.session.commit()
        return {"message": "Tag unlinked from item"}

api.add_resource(Item, "/item/<string:name>", "/item")
api.add_resource(Store, "/store/<string:name>", "/store")
api.add_resource(StoreTags, "/store/<int:store_id>/tag")
api.add_resource(Tag, "/tag/<int:tag_id>")
api.add_resource(LinkTagToItem, "/item/<int:item_id>/tag/<int:tag_id>")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
