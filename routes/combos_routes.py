from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

def create_combos_routes(db, upload_folder):
    combos_bp = Blueprint('combos', __name__)

    @combos_bp.route("/combos", methods=["POST"])
    def create_combo():
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

            combo_data = {"name": name, "price": price, "image_url": image_path}
            result = db.combos.insert_one(combo_data)
            combo_data["_id"] = str(result.inserted_id)
            return jsonify(combo_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating Combo: {str(e)}"}), 500

    @combos_bp.route("/combos", methods=["GET"])
    def get_all_combos():
        try:
            combos = db.combos.find({}, {"name": 1, "price": 1, "image_url": 1})
            combos_list = [{**combo, "_id": str(combo["_id"])} for combo in combos]
            return jsonify(combos_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching Combos: {str(e)}"}), 500

    @combos_bp.route("/combos/<id>", methods=["GET"])
    def get_combo_by_id(id):
        try:
            combo = db.combos.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            if not combo:
                return jsonify({"message": "Combo not found"}), 404
            combo["_id"] = str(combo["_id"])
            return jsonify(combo), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching Combo: {str(e)}"}), 500

    @combos_bp.route("/combos/<id>", methods=["PUT"])
    def update_combo(id):
        try:
            combo = db.combos.find_one({"_id": ObjectId(id)})
            if not combo:
                return jsonify({"message": "Combo not found"}), 404

            updated_data = request.form.to_dict()
            if "price" in updated_data:
                updated_data["price"] = float(updated_data["price"].replace(",", ""))
            if "image" in request.files:
                image = request.files.get("image")
                filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
                updated_data["image_url"] = image_path
            if "items" in updated_data:
                updated_data["items"] = updated_data["items"].split(",")  # Convert string to list if needed

            db.combos.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_combo = db.combos.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_combo["_id"] = str(updated_combo["_id"])
            return jsonify(updated_combo), 200
        except Exception as e:
            return jsonify({"message": f"Error updating Combo: {str(e)}"}), 500

    @combos_bp.route("/combos/<id>", methods=["DELETE"])
    def delete_combo(id):
        try:
            result = db.combos.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "Combo not found"}), 404
            return jsonify({"message": "Combo deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting Combo: {str(e)}"}), 500

    return combos_bp
