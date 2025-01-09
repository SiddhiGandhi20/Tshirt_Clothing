from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson import ObjectId
from models.combos_details_model import CombosDetailsModel  

# Constants for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/combos_details/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to generate the URL for the uploaded image
def generate_image_url(filename, base_url):
    return f"{base_url}uploads/combos_details/{filename}"

# Blueprint factory
def create_combos_details_routes(db):
    combos_details_bp = Blueprint('combos_details', __name__)

    # Route: Create a new combos_details
    @combos_details_bp.route("/combos_details", methods=["POST"])
    def create_combos_details():
        try:
            name = request.form.get("name")
            price = request.form.get("price")
            image = request.files.get("image")
            combo_id = request.form.get("combo_id")  # Get the combo_id from the form

            if not all([name, price, image, combo_id]):
                return jsonify({"message": "Missing required fields"}), 400

            # Ensure combo_id exists in the combos collection
            combo = db["combos"].find_one({"_id": ObjectId(combo_id)})
            if not combo:
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
            combos_details_model = CombosDetailsModel (db)
            combo_detail_id = combos_details_model.create_item(name, price, image_url, combo_id)

            if combo_detail_id:
                return jsonify({"combo_detail_id": combo_detail_id, "name": name, "price": price, "image_url": image_url}), 201
            return jsonify({"message": "Error creating combos_details"}), 500
        except Exception as e:
            return jsonify({"message": f"Error creating combos_details: {str(e)}"}), 500

    # Route: Get all combos_details
    @combos_details_bp.route("/combos_details", methods=["GET"])
    def get_all_combos_details():
        try:
            combos_details_model = CombosDetailsModel (db)
            combos_details = combos_details_model.get_all_items()
            return jsonify(combos_details), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching combos_details: {str(e)}"}), 500

    # Route: Get combos_details by ID
    @combos_details_bp.route("/combos_details/<combo_detail_id>", methods=["GET"])
    def get_combos_details_by_id(combo_detail_id):
        try:
            combos_details_model = CombosDetailsModel (db)
            combos_details = combos_details_model.get_item_by_id(combo_detail_id)
            if combos_details:
                return jsonify(combos_details), 200
            return jsonify({"message": "T-shirts details not found"}), 404
        except Exception as e:
            return jsonify({"message": f"Error fetching combos_details: {str(e)}"}), 500

    # Route: Update a combos_details
    @combos_details_bp.route("/combos_details/<combo_detail_id>", methods=["PUT"])
    def update_combos_details(combo_detail_id):
        try:
            combos_details_model = CombosDetailsModel (db)
            combos_details = combos_details_model.get_item_by_id(combo_detail_id)
            if not combos_details:
                return jsonify({"message": "T-shirts details not found"}), 404

            updated_data = request.form.to_dict()

            # Get and validate combo_id from the form data
            combo_id = updated_data.get("combo_id")
            if combo_id:
                combo = db["combos"].find_one({"_id": ObjectId(combo_id)})
                if not combo:
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
            success = combos_details_model.update_item(combo_detail_id, updated_data)
            if success:
                updated_combos_details = combos_details_model.get_item_by_id(combo_detail_id)
                return jsonify(updated_combos_details), 200
            return jsonify({"message": "Error updating combos_details"}), 500
        except Exception as e:
            return jsonify({"message": f"Error updating combos_details: {str(e)}"}), 500

    # Route: Delete a combos_details
    @combos_details_bp.route("/combos_details/<combo_detail_id>", methods=["DELETE"])
    def delete_combos_details(combo_detail_id):
        try:
            combos_details_model = CombosDetailsModel (db)
            combos_details = combos_details_model.get_item_by_id(combo_detail_id)
            if not combos_details:
                return jsonify({"message": "T-shirts details not found"}), 404

            success = combos_details_model.delete_item(combo_detail_id)
            if success:
                return jsonify({"message": "T-shirts details deleted successfully"}), 200
            return jsonify({"message": "Error deleting combos_details"}), 500
        except Exception as e:
            return jsonify({"message": f"Error deleting combos_details: {str(e)}"}), 500

    return combos_details_bp
