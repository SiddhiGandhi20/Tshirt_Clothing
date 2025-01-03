from bson import ObjectId

class ComboModel:
    def __init__(self, db):
        self.collection = db.combos  # Reference to the 'combos' collection in MongoDB

    def create_combo(self, data):
        try:
            combo_data = {
                "name": data["name"],
                "price": float(data["price"].replace(",", "")),  # Handle commas in price
                "image_url": data["image_url"],
            }
            result = self.collection.insert_one(combo_data)
            return {"message": "Combo created successfully", "combo_id": str(result.inserted_id)}, 201
        except Exception as e:
            return {"message": "Error creating Combo", "error": str(e)}, 500

    def get_combo_by_id(self, combo_id):
        try:
            combo = self.collection.find_one({"_id": ObjectId(combo_id)})
            if combo:
                combo["_id"] = str(combo["_id"])
                return combo, 200
            return {"message": "Combo not found"}, 404
        except Exception as e:
            return {"message": "Error fetching combo", "error": str(e)}, 500

    def get_all_combos(self):
        try:
            combos = list(self.collection.find({}, {"name": 1, "price": 1, "image_url": 1}))
            for combo in combos:
                combo["_id"] = str(combo["_id"])
            return combos, 200
        except Exception as e:
            return {"message": "Error fetching combos", "error": str(e)}, 500

    def update_combo(self, combo_id, data):
        try:
            update_data = {key: value for key, value in data.items() if value is not None}
            if "price" in update_data:
                update_data["price"] = float(update_data["price"].replace(",", ""))

            result = self.collection.update_one({"_id": ObjectId(combo_id)}, {"$set": update_data})
            if result.modified_count == 0:
                return {"message": "Combo not found or no changes made"}, 404

            updated_combo = self.collection.find_one({"_id": ObjectId(combo_id)})
            updated_combo["_id"] = str(updated_combo["_id"])
            return updated_combo, 200
        except Exception as e:
            return {"message": "Error updating combo", "error": str(e)}, 500

    def delete_combo(self, combo_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(combo_id)})
            if result.deleted_count == 0:
                return {"message": "Combo not found"}, 404
            return {"message": "Combo deleted successfully"}, 200
        except Exception as e:
            return {"message": "Error deleting combo", "error": str(e)}, 500
