from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

# Constants
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/combos/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to generate the URL for the uploaded image
def generate_image_url(filename, base_url):
    return f"{base_url}uploads/combos/{filename}"

# Blueprint factory
def create_combos_routes(db):
    combos_bp = Blueprint('combos', __name__)

    # Route: Create a Combos item
    @combos_bp.route("/combos", methods=["POST"])
    def create_combos():
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

            if not allowed_file(image.filename):
                return jsonify({"message": "Invalid image file type"}), 400

            # Save the image
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

            # Generate image URL
            base_url = request.host_url
            image_url = generate_image_url(filename, base_url)

            # Insert into database
            combo_data = {"name": name, "price": price, "image_url": image_url}
            result = db.combos.insert_one(combo_data)
            combo_data["_id"] = str(result.inserted_id)

            return jsonify(combo_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating combo: {str(e)}"}), 500

    # Route: Fetch all combos
    @combos_bp.route("/combos", methods=["GET"])
    def get_all_combos():
        try:
            combos = db.combos.find({}, {"name": 1, "price": 1, "image_url": 1})
            combos_list = [
                {"_id": str(h["_id"]), "name": h["name"], "price": h["price"], "image_url": h["image_url"]}
                for h in combos
            ]
            return jsonify(combos_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching combos: {str(e)}"}), 500

    # Route: Fetch combo by ID
    @combos_bp.route("/combos/<id>", methods=["GET"])
    def get_combo_by_id(id):
        try:
            combo = db.combos.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            if not combo :
                return jsonify({"message": "Combos not found"}), 404
            combo ["_id"] = str(combo ["_id"])
            return jsonify(combo ), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching combo: {str(e)}"}), 500

    # Route: Update a combo item
    @combos_bp.route("/combos/<id>", methods=["PUT"])
    def update_combos(id):
        try:
            combo  = db.combos.find_one({"_id": ObjectId(id)})
            if not combo :
                return jsonify({"message": "Combos not found"}), 404

            updated_data = request.form.to_dict()
            if "price" in updated_data:
                updated_data["price"] = float(updated_data["price"].replace(",", ""))

            if "image" in request.files:
                image = request.files["image"]
                if not allowed_file(image.filename):
                    return jsonify({"message": "Invalid image file type"}), 400

                filename = secure_filename(image.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(image_path)
                base_url = request.host_url
                updated_data["image_url"] = generate_image_url(filename, base_url)

            db.combos.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_combo = db.combos.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_combo["_id"] = str(updated_combo["_id"])

            return jsonify(updated_combo), 200
        except Exception as e:
            return jsonify({"message": f"Error updating combo: {str(e)}"}), 500

    # Route: Delete a combo item
    @combos_bp.route("/combos/<id>", methods=["DELETE"])
    def delete_combo(id):
        try:
            result = db.combos.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "Combo not found"}), 404
            return jsonify({"message": "Combo deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting combo: {str(e)}"}), 500

    @combos_bp.route("/uploads/combos/<filename>")
    def serve_image(filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except FileNotFoundError:
            return jsonify({"message": "File not found"}), 404



    return combos_bp
