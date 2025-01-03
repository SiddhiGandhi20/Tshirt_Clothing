from bson import ObjectId

class HoodieModel:
    def __init__(self, db):
        self.collection = db.hoodies  # Reference to the 'hoodies' collection in MongoDB

    def create_hoodie(self, data):
        try:
            hoodie_data = {
                "name": data["name"],
                "price": float(data["price"].replace(",", "")),  # Handle commas in price
                "image_url": data["image_url"],
            }
            result = self.collection.insert_one(hoodie_data)
            return {"message": "Hoodie created successfully", "hoodie_id": str(result.inserted_id)}, 201
        except Exception as e:
            return {"message": "Error creating Hoodie", "error": str(e)}, 500

    def get_product_by_id(self, product_id):
        try:
            product = self.collection.find_one({"_id": ObjectId(product_id)})
            if product:
                product["_id"] = str(product["_id"])
                return product, 200
            return {"message": "Product not found"}, 404
        except Exception as e:
            return {"message": "Error fetching product", "error": str(e)}, 500

    def get_all_products(self):
        try:
            products = list(self.collection.find({}, {"name": 1, "price": 1, "image_url": 1}))
            for product in products:
                product["_id"] = str(product["_id"])
            return products, 200
        except Exception as e:
            return {"message": "Error fetching products", "error": str(e)}, 500

    def update_product(self, product_id, data):
        try:
            update_data = {key: value for key, value in data.items() if value is not None}
            if "price" in update_data:
                update_data["price"] = float(update_data["price"].replace(",", ""))

            result = self.collection.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
            if result.modified_count == 0:
                return {"message": "Product not found or no changes made"}, 404

            updated_product = self.collection.find_one({"_id": ObjectId(product_id)})
            updated_product["_id"] = str(updated_product["_id"])
            return updated_product, 200
        except Exception as e:
            return {"message": "Error updating product", "error": str(e)}, 500

    def delete_product(self, product_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(product_id)})
            if result.deleted_count == 0:
                return {"message": "Product not found"}, 404
            return {"message": "Product deleted successfully"}, 200
        except Exception as e:
            return {"message": "Error deleting product", "error": str(e)}, 500
