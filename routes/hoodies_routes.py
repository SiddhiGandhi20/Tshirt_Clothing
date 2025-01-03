from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

def create_hoodies_routes(db, upload_folder):
    hoodies_bp = Blueprint('hoodies', __name__)

    @hoodies_bp.route("/hoodies", methods=["POST"])
    def create_hoodie():
        try:
            name = request.form.get("name")
            price = request.form.get("price")
            image = request.files.get("image")

            if not all([name, price, image]):
                return jsonify({"message": "Missing required fields"}), 400

            try:
                price = float(price.replace(",", ""))
            except ValueError:
                return jsonify({"message": "Invalid price format"}), 400

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filename = secure_filename(image.filename)
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)

            hoodie_data = {"name": name, "price": price, "image_url": image_path}
            result = db.hoodies.insert_one(hoodie_data)
            hoodie_data["_id"] = str(result.inserted_id)
            return jsonify(hoodie_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating Hoodie: {str(e)}"}), 500

    @hoodies_bp.route("/hoodies", methods=["GET"])
    def get_all_hoodies():
        try:
            hoodies = db.hoodies.find({}, {"name": 1, "price": 1, "image_url": 1})
            hoodies_list = [{**h, "_id": str(h["_id"])} for h in hoodies]
            return jsonify(hoodies_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching Hoodies: {str(e)}"}), 500

    @hoodies_bp.route("/hoodies/<id>", methods=["GET"])
    def get_hoodie_by_id(id):
        try:
            hoodie = db.hoodies.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            if not hoodie:
                return jsonify({"message": "Hoodie not found"}), 404
            hoodie["_id"] = str(hoodie["_id"])
            return jsonify(hoodie), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching Hoodie: {str(e)}"}), 500

    @hoodies_bp.route("/hoodies/<id>", methods=["PUT"])
    def update_hoodie(id):
        try:
            hoodie = db.hoodies.find_one({"_id": ObjectId(id)})
            if not hoodie:
                return jsonify({"message": "Hoodie not found"}), 404

            updated_data = request.form.to_dict()
            if "price" in updated_data:
                updated_data["price"] = float(updated_data["price"].replace(",", ""))
            if "image" in request.files:
                image = request.files.get("image")
                filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
                updated_data["image_url"] = image_path

            db.hoodies.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_hoodie = db.hoodies.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_hoodie["_id"] = str(updated_hoodie["_id"])
            return jsonify(updated_hoodie), 200
        except Exception as e:
            return jsonify({"message": f"Error updating Hoodie: {str(e)}"}), 500

    @hoodies_bp.route("/hoodies/<id>", methods=["DELETE"])
    def delete_hoodie(id):
        try:
            result = db.hoodies.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "Hoodie not found"}), 404
            return jsonify({"message": "Hoodie deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting Hoodie: {str(e)}"}), 500

    return hoodies_bp
