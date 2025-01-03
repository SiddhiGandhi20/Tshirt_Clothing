from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

def create_tshirts_routes(db, upload_folder):
    tshirts_bp = Blueprint('tshirts', __name__)

    # POST: Create a new T-shirt
    @tshirts_bp.route("/tshirts", methods=["POST"])
    def create_tshirt():
        try:
            # Extract data
            name = request.form.get("name")
            price = request.form.get("price")
            image = request.files.get("image")

            # Validate required fields
            if not all([name, price, image]):
                return jsonify({"message": "Missing required fields"}), 400

            # Remove commas from the price and convert to float
            try:
                price = float(price.replace(",", ""))
            except ValueError:
                return jsonify({"message": "Invalid price format"}), 400

            # Save image
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filename = secure_filename(image.filename)
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)

            # Create T-shirt data
            tshirt_data = {
                "name": name,
                "price": price,
                "image_url": image_path
            }

            # Insert into MongoDB
            result = db.tshirts.insert_one(tshirt_data)
            tshirt_data["_id"] = str(result.inserted_id)  # Include ID in the response
            return jsonify(tshirt_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating T-shirt: {str(e)}"}), 500

    # GET: Fetch all T-shirts
    @tshirts_bp.route("/tshirts", methods=["GET"])
    def get_all_tshirts():
        try:
            tshirts = db.tshirts.find({}, {"name": 1, "price": 1, "image_url": 1})
            tshirts_list = [{**t, "_id": str(t["_id"])} for t in tshirts]  # Serialize ObjectId
            return jsonify(tshirts_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching T-shirts: {str(e)}"}), 500

    # GET: Fetch a T-shirt by ID
    @tshirts_bp.route("/tshirts/<id>", methods=["GET"])
    def get_tshirt_by_id(id):
        try:
            tshirt = db.tshirts.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            if not tshirt:
                return jsonify({"message": "T-shirt not found"}), 404
            tshirt["_id"] = str(tshirt["_id"])  # Serialize ObjectId
            return jsonify(tshirt), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching T-shirt: {str(e)}"}), 500

    # PUT: Update a T-shirt by ID
    @tshirts_bp.route("/tshirts/<id>", methods=["PUT"])
    def update_tshirt(id):
        try:
            # Extract T-shirt to update
            tshirt = db.tshirts.find_one({"_id": ObjectId(id)})
            if not tshirt:
                return jsonify({"message": "T-shirt not found"}), 404

            # Extract updated data
            updated_data = request.form.to_dict()
            if "price" in updated_data:
                updated_data["price"] = float(updated_data["price"].replace(",", ""))
            if "image" in request.files:
                image = request.files.get("image")
                filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
                updated_data["image_url"] = image_path

            # Update in MongoDB
            db.tshirts.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_tshirt = db.tshirts.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_tshirt["_id"] = str(updated_tshirt["_id"])
            return jsonify(updated_tshirt), 200
        except Exception as e:
            return jsonify({"message": f"Error updating T-shirt: {str(e)}"}), 500

    # DELETE: Delete a T-shirt by ID
    @tshirts_bp.route("/tshirts/<id>", methods=["DELETE"])
    def delete_tshirt(id):
        try:
            result = db.tshirts.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "T-shirt not found"}), 404
            return jsonify({"message": "T-shirt deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting T-shirt: {str(e)}"}), 500

    return tshirts_bp
