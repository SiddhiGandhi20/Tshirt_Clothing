from pymongo.errors import PyMongoError
from bson import ObjectId

class CombosDetailsModel:
    def __init__(self, db):
        self.collection = db["combos_details"]

    # CREATE: Add a new product
    def create_item(self, name, price, image_url, combo_id):
        try:
            # Handle different data types for price
            if isinstance(price, str):  
                price = float(price.replace(",", ""))  # Remove commas and convert to float
            elif isinstance(price, (int, float)):
                price = float(price)  # Ensure price is a float
            else:
                raise ValueError("Invalid price format. Must be a string, int, or float.")

            item = {
                "name": name,
                "price": price,
                "image_url": image_url,
                "combo_id": combo_id
            }
            result = self.collection.insert_one(item)
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Error creating item: {e}")
            return None


    # READ: Get all products
    def get_all_items(self):
        try:
            items = self.collection.find()
            return [
                {
                    "combo_detail_id": str(item["_id"]),
                    "name": item["name"],
                    "price": item["price"],
                    "image_url": item["image_url"],
                    "combo_id": str(item["combo_id"])
                }
                for item in items
            ]
        except PyMongoError as e:
            print(f"Error retrieving items: {e}")
            return []

    # READ: Get a product by ID
    def get_item_by_id(self, item_id):
        try:
            item = self.collection.find_one({"combo_id": str(item_id)})
            if item:
                return {
                    "combo_detail_id": str(item["_id"]),
                    "name": item["name"],
                    "price": item["price"],
                    "image_url": item["image_url"],
                    "combo_id": str(item["combo_id"])
                }
            return None
        except PyMongoError as e:
            print(f"Error retrieving item: {e}")
            return None

    # UPDATE: Update product details
    def update_item(self, item_id, update_data):
        try:
            if "price" in update_data:
                price = update_data["price"]
                if isinstance(price, str):  # If it's a string, apply the replace method
                    update_data["price"] = float(price.replace(",", ""))  # Remove commas and convert to float
                elif isinstance(price, (int, float)):  # If it's already a number (int or float), keep it
                    update_data["price"] = float(price)  # Convert to float just in case
                else:
                    raise ValueError("Invalid price format")

            result = self.collection.update_one(
                {"_id": ObjectId(item_id)}, {"$set": update_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            print(f"Error updating item: {e}")
            return False
        except ValueError as ve:
            print(f"Error updating item: {ve}")
            return False

    # DELETE: Delete a product
    def delete_item(self, item_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(item_id)})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error deleting item: {e}")
            return False

