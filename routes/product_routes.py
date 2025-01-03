from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

def create_product_routes(db, upload_folder):
    product_bp = Blueprint('products', __name__)

    # Helper to serialize ObjectId
    def serialize_objectid(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return obj

    # POST: Create a new Product
    @product_bp.route("/products", methods=["POST"])
    def create_product():
        try:
            # Extract data
            name = request.form.get("name")
            price = request.form.get("price")
            image = request.files.get("image")

            # Validate required fields
            if not all([name, price, image]):
                return jsonify({"message": "Missing required fields"}), 400

            # Save image
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filename = secure_filename(image.filename)
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)

            # Create product data
            product_data = {
                "name": name,
                "price": float(price),
                "image_url": image_path
            }

            # Insert into MongoDB
            result = db.products.insert_one(product_data)
            product_data["_id"] = str(result.inserted_id)  # Include ID in the response
            return jsonify(product_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating product: {str(e)}"}), 500

    # GET: Fetch all products
    @product_bp.route("/products", methods=["GET"])
    def get_all_products():
        try:
            products = db.products.find({}, {"name": 1, "price": 1, "image_url": 1})
            products_list = [{**p, "_id": str(p["_id"])} for p in products]  # Serialize ObjectId
            return jsonify(products_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching products: {str(e)}"}), 500

    # GET: Fetch a product by ID
    @product_bp.route("/products/<id>", methods=["GET"])
    def get_product_by_id(id):
        try:
            product = db.products.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            if not product:
                return jsonify({"message": "Product not found"}), 404
            product["_id"] = str(product["_id"])  # Serialize ObjectId
            return jsonify(product), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching product: {str(e)}"}), 500

    # PUT: Update a product by ID
    @product_bp.route("/products/<id>", methods=["PUT"])
    def update_product(id):
        try:
            # Extract product to update
            product = db.products.find_one({"_id": ObjectId(id)})
            if not product:
                return jsonify({"message": "Product not found"}), 404

            # Extract updated data
            updated_data = request.form.to_dict()
            if "price" in updated_data:
                updated_data["price"] = float(updated_data["price"])
            if "image" in request.files:
                image = request.files.get("image")
                filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
                updated_data["image_url"] = image_path

            # Update in MongoDB
            db.products.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_product = db.products.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_product["_id"] = str(updated_product["_id"])
            return jsonify(updated_product), 200
        except Exception as e:
            return jsonify({"message": f"Error updating product: {str(e)}"}), 500

    # DELETE: Delete a product by ID
    @product_bp.route("/products/<id>", methods=["DELETE"])
    def delete_product(id):
        try:
            result = db.products.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "Product not found"}), 404
            return jsonify({"message": "Product deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting product: {str(e)}"}), 500

    return product_bp
