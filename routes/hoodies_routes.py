from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

# Constants
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/hoodies/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to generate the URL for the uploaded image
def generate_image_url(filename, base_url):
    return f"{base_url}uploads/hoodies/{filename}"

# Blueprint factory
def create_hoodies_routes(db):
    hoodies_bp = Blueprint('hoodies', __name__)

    # Route: Create a new Hoodie item
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
            hoodie_data = {"name": name, "price": price, "image_url": image_url}
            result = db.hoodies.insert_one(hoodie_data)
            hoodie_data["_id"] = str(result.inserted_id)

            return jsonify(hoodie_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating Hoodie: {str(e)}"}), 500

    # Route: Fetch all Hoodies
    @hoodies_bp.route("/hoodies", methods=["GET"])
    def get_all_hoodies():
        try:
            hoodies = db.hoodies.find({}, {"name": 1, "price": 1, "image_url": 1})
            hoodies_list = [
                {"_id": str(h["_id"]), "name": h["name"], "price": h["price"], "image_url": h["image_url"]}
                for h in hoodies
            ]
            return jsonify(hoodies_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching Hoodies: {str(e)}"}), 500

    # Route: Fetch Hoodie by ID
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

    # Route: Update a Hoodie item
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
                image = request.files["image"]
                if not allowed_file(image.filename):
                    return jsonify({"message": "Invalid image file type"}), 400

                filename = secure_filename(image.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(image_path)
                base_url = request.host_url
                updated_data["image_url"] = generate_image_url(filename, base_url)

            db.hoodies.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_hoodie = db.hoodies.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_hoodie["_id"] = str(updated_hoodie["_id"])

            return jsonify(updated_hoodie), 200
        except Exception as e:
            return jsonify({"message": f"Error updating Hoodie: {str(e)}"}), 500

    # Route: Delete a Hoodie item
    @hoodies_bp.route("/hoodies/<id>", methods=["DELETE"])
    def delete_hoodie(id):
        try:
            result = db.hoodies.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "Hoodie not found"}), 404
            return jsonify({"message": "Hoodie deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting Hoodie: {str(e)}"}), 500

    @hoodies_bp.route("/uploads/hoodies/<filename>")
    def serve_image(filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except FileNotFoundError:
            return jsonify({"message": "File not found"}), 404



    return hoodies_bp
