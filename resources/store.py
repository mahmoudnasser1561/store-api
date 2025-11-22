import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
# from db import stores
from schemas import StoreSchema, ItemSchema
from models import StoreModel, ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


blp = Blueprint("Stores", "stores", description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(cls, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store
    
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return {"Message": "store deleted"}

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(cls):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(cls, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, 
                message="A store with that same name already exists."
                )
        except SQLAlchemyError:
            abort(500, 
                message="An Error happened while inserting the store."
                )

        return store


@blp.route("/store/search")
class StoreSearch(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        name = request.args.get("name")
        if not name:
            abort(400, message="Provide ?name=<term>")
        return StoreModel.query.filter(StoreModel.name.ilike(f"%{name}%")).all()
    
@blp.route("/store/<int:store_id>/count")
class StoreItemCount(MethodView):
    @blp.response(200)
    def get(self, store_id):
        count = ItemModel.query.filter_by(store_id=store_id).count()
        return {"store_id": store_id, "item_count": count}
    
@blp.route("/store/<int:store_id>/item/<int:item_id>")
class StoreItem(MethodView):
    """Link or unlink an item to a store"""

    @blp.response(200)
    def delete(self, store_id, item_id):
        """Unlink a specific item from a store by assigning it to 'Unassigned'."""
        
        item = ItemModel.query.get_or_404(item_id)

        if item.store_id != store_id:
            abort(404, message="Item not found under this store")

        UNASSIGNED_ID = 0
        item.store_id = UNASSIGNED_ID
        db.session.commit()

        return {"message": "Item moved to Unassigned store", "item": ItemSchema().dump(item)}
    

    @blp.response(200)
    def put(self, store_id, item_id):
        """link a specific item to a specific store."""

        item = ItemModel.query.get_or_404(item_id)
        store = StoreModel.query.get_or_404(store_id)

        if item.store_id == store_id:
            return {"message": "Item already assigned to this store", "item": ItemSchema().dump(item)}
        
        item.store_id = store_id
        db.session.commit()

        return {"message": "Item linked to store", "item": ItemSchema().dump(item)}