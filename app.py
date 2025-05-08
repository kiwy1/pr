from flask import Flask, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from db import db
from models import StoreModel, ItemModel, TagModel, UserModel
from schemas import ItemSchema, StoreSchema, TagSchema, UserSchema

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "A#135@!ajdqiIhgn1239123!@9741mfA"
api = Api(app)
db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

item_schema = ItemSchema()
store_schema = StoreSchema()
tag_schema = TagSchema()
user_schema = UserSchema()
tags_schema = TagSchema(many=True)

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        user = UserModel(username=data["username"])
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return {"message": "User registered successfully"}, 200

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user = UserModel.query.filter_by(username=data["username"]).first()
        if user and user.check_password(data["password"]):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}, 200
        return {"message": "Invalid credentials"}, 401

class Item(Resource):
    @jwt_required()
    def get(self, name):
        item = ItemModel.query.filter_by(name=name).first()
        if item:
            return item_schema.dump(item)
        return {"message": "Item not found"}, 404

    @jwt_required()
    def post(self):
        data = request.get_json()
        item = ItemModel(**data)
        db.session.add(item)
        db.session.commit()
        return item_schema.dump(item)

    @jwt_required()
    def delete(self, name):
        item = ItemModel.query.filter_by(name=name).first()
        if item:
            db.session.delete(item)
            db.session.commit()
        return {"message": "Item deleted"}

class Store(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        store = StoreModel(**data)
        db.session.add(store)
        db.session.commit()
        return store_schema.dump(store)

    @jwt_required()
    def get(self, name):
        store = StoreModel.query.filter_by(name=name).first()
        if store:
            return store_schema.dump(store)
        return {"message": "Store not found"}, 404

class StoreTags(Resource):
    @jwt_required()
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return tags_schema.dump(store.tags.all())

    @jwt_required()
    def post(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        data = request.get_json()
        tag = TagModel(name=data["name"], store_id=store.id)
        db.session.add(tag)
        db.session.commit()
        return tag_schema.dump(tag)

class Tag(Resource):
    @jwt_required()
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag_schema.dump(tag)

    @jwt_required()
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if tag.items:
            return {"message": "Cannot delete tag with associated items"}, 400
        db.session.delete(tag)
        db.session.commit()
        return {"message": "Tag deleted"}

class LinkTagToItem(Resource):
    @jwt_required()
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        if tag not in item.tags:
            item.tags.append(tag)
            db.session.commit()
        return {"message": "Tag linked to item"}

    @jwt_required()
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        if tag in item.tags:
            item.tags.remove(tag)
            db.session.commit()
        return {"message": "Tag unlinked from item"}

api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(Item, "/item/<string:name>", "/item")
api.add_resource(Store, "/store/<string:name>", "/store")
api.add_resource(StoreTags, "/store/<int:store_id>/tag")
api.add_resource(Tag, "/tag/<int:tag_id>")
api.add_resource(LinkTagToItem, "/item/<int:item_id>/tag/<int:tag_id>")

if __name__ == "__main__":
    app.run(debug=True)
