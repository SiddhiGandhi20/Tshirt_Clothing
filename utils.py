import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle ObjectId."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)
