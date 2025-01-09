from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson import ObjectId
from models.hoodies_details_models import HoodiesDetailsModel  

# Constants for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/hoodies_details/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to generate the URL for the uploaded image
def generate_image_url(filename, base_url):
    return f"{base_url}uploads/hoodies_details/{filename}"

# Blueprint factory
def create_hoodies_details_routes(db):
    hoodies_details_bp = Blueprint('hoodies_details', __name__)

    # Route: Create a new hoodies_details
    @hoodies_details_bp.route("/hoodies_details", methods=["POST"])
    def create_hoodies_details():
        try:
            name = request.form.get("name")
            price = request.form.get("price")
            image = request.files.get("image")
            hoodie_id = request.form.get("hoodie_id")  # Get the hoodie_id from the form

            if not all([name, price, image, hoodie_id]):
                return jsonify({"message": "Missing required fields"}), 400

            # Ensure hoodie_id exists in the hoodies collection
            hoodie = db["hoodies"].find_one({"_id": ObjectId(hoodie_id)})
            if not hoodie:
                return jsonify({"message": "T-shirt not found"}), 404

            if not allowed_file(image.filename):
                return jsonify({"message": "Invalid image file type"}), 400

            # Save the image
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

            # Generate image URL
            base_url = request.host_url
            image_url = generate_image_url(filename, base_url)

            # Remove commas from price and convert to float
            try:
                price = float(price.replace(",", ""))
            except ValueError:
                return jsonify({"message": "Invalid price format"}), 400

            # Insert into database
            hoodies_details_model = HoodiesDetailsModel(db)
            hoodie_detail_id = hoodies_details_model.create_item(name, price, image_url, hoodie_id)

            if hoodie_detail_id:
                return jsonify({"hoodie_detail_id": hoodie_detail_id, "name": name, "price": price, "image_url": image_url}), 201
            return jsonify({"message": "Error creating hoodies_details"}), 500
        except Exception as e:
            return jsonify({"message": f"Error creating hoodies_details: {str(e)}"}), 500

    # Route: Get all hoodies_details
    @hoodies_details_bp.route("/hoodies_details", methods=["GET"])
    def get_all_hoodies_details():
        try:
            hoodies_details_model = HoodiesDetailsModel(db)
            hoodies_details = hoodies_details_model.get_all_items()
            return jsonify(hoodies_details), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching hoodies_details: {str(e)}"}), 500

    # Route: Get hoodies_details by ID
    @hoodies_details_bp.route("/hoodies_details/<hoodie_detail_id>", methods=["GET"])
    def get_hoodies_details_by_id(hoodie_detail_id):
        try:
            hoodies_details_model = HoodiesDetailsModel(db)
            hoodies_details = hoodies_details_model.get_item_by_id(hoodie_detail_id)
            if hoodies_details:
                return jsonify(hoodies_details), 200
            return jsonify({"message": "T-shirts details not found"}), 404
        except Exception as e:
            return jsonify({"message": f"Error fetching hoodies_details: {str(e)}"}), 500

    # Route: Update a hoodies_details
    @hoodies_details_bp.route("/hoodies_details/<hoodie_detail_id>", methods=["PUT"])
    def update_hoodies_details(hoodie_detail_id):
        try:
            hoodies_details_model = HoodiesDetailsModel(db)
            hoodies_details = hoodies_details_model.get_item_by_id(hoodie_detail_id)
            if not hoodies_details:
                return jsonify({"message": "T-shirts details not found"}), 404

            updated_data = request.form.to_dict()

            # Get and validate hoodie_id from the form data
            hoodie_id = updated_data.get("hoodie_id")
            if hoodie_id:
                hoodie = db["hoodies"].find_one({"_id": ObjectId(hoodie_id)})
                if not hoodie:
                    return jsonify({"message": "T-shirt not found"}), 404

            # Update price and handle commas if present
            if "price" in updated_data:
                try:
                    updated_data["price"] = float(updated_data["price"].replace(",", ""))
                except ValueError:
                    return jsonify({"message": "Invalid price format"}), 400

            # Update image if present
            if "image" in request.files:
                image = request.files["image"]
                if not allowed_file(image.filename):
                    return jsonify({"message": "Invalid image file type"}), 400

                filename = secure_filename(image.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(image_path)
                base_url = request.host_url
                updated_data["image_url"] = generate_image_url(filename, base_url)

            # Update in database
            success = hoodies_details_model.update_item(hoodie_detail_id, updated_data)
            if success:
                updated_hoodies_details = hoodies_details_model.get_item_by_id(hoodie_detail_id)
                return jsonify(updated_hoodies_details), 200
            return jsonify({"message": "Error updating hoodies_details"}), 500
        except Exception as e:
            return jsonify({"message": f"Error updating hoodies_details: {str(e)}"}), 500

    # Route: Delete a hoodies_details
    @hoodies_details_bp.route("/hoodies_details/<hoodie_detail_id>", methods=["DELETE"])
    def delete_hoodies_details(hoodie_detail_id):
        try:
            hoodies_details_model = HoodiesDetailsModel(db)
            hoodies_details = hoodies_details_model.get_item_by_id(hoodie_detail_id)
            if not hoodies_details:
                return jsonify({"message": "T-shirts details not found"}), 404

            success = hoodies_details_model.delete_item(hoodie_detail_id)
            if success:
                return jsonify({"message": "T-shirts details deleted successfully"}), 200
            return jsonify({"message": "Error deleting hoodies_details"}), 500
        except Exception as e:
            return jsonify({"message": f"Error deleting hoodies_details: {str(e)}"}), 500

    return hoodies_details_bp
