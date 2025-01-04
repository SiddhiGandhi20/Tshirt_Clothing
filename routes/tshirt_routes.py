from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

# Constants
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/tshirts/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to generate the URL for the uploaded image
def generate_image_url(filename, base_url):
    return f"{base_url}uploads/tshirts/{filename}"

# Blueprint factory
def create_tshirts_routes(db):
    tshirts_bp = Blueprint('tshirts', __name__)

    # Route: Create a tshirts item
    @tshirts_bp.route("/tshirts", methods=["POST"])
    def create_tshirts():
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
            tshirt_data = {"name": name, "price": price, "image_url": image_url}
            result = db.tshirts.insert_one(tshirt_data)
            tshirt_data["_id"] = str(result.inserted_id)

            return jsonify(tshirt_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating tshirt: {str(e)}"}), 500

    # Route: Fetch all tshirts
    @tshirts_bp.route("/tshirts", methods=["GET"])
    def get_all_tshirts():
        try:
            tshirts = db.tshirts.find({}, {"name": 1, "price": 1, "image_url": 1})
            tshirts_list = [
                {"_id": str(h["_id"]), "name": h["name"], "price": h["price"], "image_url": h["image_url"]}
                for h in tshirts
            ]
            return jsonify(tshirts_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching tshirts: {str(e)}"}), 500

    # Route: Fetch tshirt by ID
    @tshirts_bp.route("/tshirts/<id>", methods=["GET"])
    def get_combo_by_id(id):
        try:
            tshirt = db.tshirts.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            if not tshirt:
                return jsonify({"message": "tshirts not found"}), 404
            tshirt["_id"] = str(tshirt["_id"])
            return jsonify(tshirt), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching tshirt: {str(e)}"}), 500

    # Route: Update a tshirt item
    @tshirts_bp.route("/tshirts/<id>", methods=["PUT"])
    def update_tshirts(id):
        try:
            tshirt = db.tshirts.find_one({"_id": ObjectId(id)})
            if not tshirt:
                return jsonify({"message": "tshirts not found"}), 404

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

            db.tshirts.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_tshirt = db.tshirts.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_tshirt["_id"] = str(updated_tshirt["_id"])

            return jsonify(updated_tshirt), 200
        except Exception as e:
            return jsonify({"message": f"Error updating tshirt: {str(e)}"}), 500

    # Route: Delete a tshirt item
    @tshirts_bp.route("/tshirts/<id>", methods=["DELETE"])
    def delete_combo(id):
        try:
            result = db.tshirts.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "Combo not found"}), 404
            return jsonify({"message": "Combo deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting tshirt: {str(e)}"}), 500

    @tshirts_bp.route("/uploads/tshirts/<filename>")
    def serve_image(filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except FileNotFoundError:
            return jsonify({"message": "File not found"}), 404



    return tshirts_bp
