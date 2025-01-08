from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson import ObjectId
from models.tshirt_details_model import TshirtsDetailsModel  # Import TshirtsDetailsModel

# Constants for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/tshirts_details/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to generate the URL for the uploaded image
def generate_image_url(filename, base_url):
    return f"{base_url}uploads/tshirts_details/{filename}"

# Blueprint factory
def create_tshirts_details_routes(db):
    tshirts_details_bp = Blueprint('tshirts_details', __name__)

    # Route: Create a new tshirts_details
    @tshirts_details_bp.route("/tshirts_details", methods=["POST"])
    def create_tshirts_details():
        try:
            name = request.form.get("name")
            price = request.form.get("price")
            image = request.files.get("image")
            tshirt_id = request.form.get("tshirt_id")  # Get the tshirt_id from the form

            if not all([name, price, image, tshirt_id]):
                return jsonify({"message": "Missing required fields"}), 400

            # Ensure tshirt_id exists in the tshirts collection
            tshirt = db["tshirts"].find_one({"_id": ObjectId(tshirt_id)})
            if not tshirt:
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
            tshirts_details_model = TshirtsDetailsModel(db)
            tshirt_detail_id = tshirts_details_model.create_item(name, price, image_url, tshirt_id)

            if tshirt_detail_id:
                return jsonify({"tshirt_detail_id": tshirt_detail_id, "name": name, "price": price, "image_url": image_url}), 201
            return jsonify({"message": "Error creating tshirts_details"}), 500
        except Exception as e:
            return jsonify({"message": f"Error creating tshirts_details: {str(e)}"}), 500

    # Route: Get all tshirts_details
    @tshirts_details_bp.route("/tshirts_details", methods=["GET"])
    def get_all_tshirts_details():
        try:
            tshirts_details_model = TshirtsDetailsModel(db)
            tshirts_details = tshirts_details_model.get_all_items()
            return jsonify(tshirts_details), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching tshirts_details: {str(e)}"}), 500

    # Route: Get tshirts_details by ID
    @tshirts_details_bp.route("/tshirts_details/<tshirt_detail_id>", methods=["GET"])
    def get_tshirts_details_by_id(tshirt_detail_id):
        try:
            tshirts_details_model = TshirtsDetailsModel(db)
            tshirts_details = tshirts_details_model.get_item_by_id(tshirt_detail_id)
            if tshirts_details:
                return jsonify(tshirts_details), 200
            return jsonify({"message": "T-shirts details not found"}), 404
        except Exception as e:
            return jsonify({"message": f"Error fetching tshirts_details: {str(e)}"}), 500

    # Route: Update a tshirts_details
    @tshirts_details_bp.route("/tshirts_details/<tshirt_detail_id>", methods=["PUT"])
    def update_tshirts_details(tshirt_detail_id):
        try:
            tshirts_details_model = TshirtsDetailsModel(db)
            tshirts_details = tshirts_details_model.get_item_by_id(tshirt_detail_id)
            if not tshirts_details:
                return jsonify({"message": "T-shirts details not found"}), 404

            updated_data = request.form.to_dict()

            # Get and validate tshirt_id from the form data
            tshirt_id = updated_data.get("tshirt_id")
            if tshirt_id:
                tshirt = db["tshirts"].find_one({"_id": ObjectId(tshirt_id)})
                if not tshirt:
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
            success = tshirts_details_model.update_item(tshirt_detail_id, updated_data)
            if success:
                updated_tshirts_details = tshirts_details_model.get_item_by_id(tshirt_detail_id)
                return jsonify(updated_tshirts_details), 200
            return jsonify({"message": "Error updating tshirts_details"}), 500
        except Exception as e:
            return jsonify({"message": f"Error updating tshirts_details: {str(e)}"}), 500

    # Route: Delete a tshirts_details
    @tshirts_details_bp.route("/tshirts_details/<tshirt_detail_id>", methods=["DELETE"])
    def delete_tshirts_details(tshirt_detail_id):
        try:
            tshirts_details_model = TshirtsDetailsModel(db)
            tshirts_details = tshirts_details_model.get_item_by_id(tshirt_detail_id)
            if not tshirts_details:
                return jsonify({"message": "T-shirts details not found"}), 404

            success = tshirts_details_model.delete_item(tshirt_detail_id)
            if success:
                return jsonify({"message": "T-shirts details deleted successfully"}), 200
            return jsonify({"message": "Error deleting tshirts_details"}), 500
        except Exception as e:
            return jsonify({"message": f"Error deleting tshirts_details: {str(e)}"}), 500

    return tshirts_details_bp
