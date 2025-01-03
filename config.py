import os

class Config:
    # Use local MongoDB server
    MONGO_URI = "mongodb://127.0.0.1:27017/tshirt_clothing"
    
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Folder to store images
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions for images
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max upload size of 16MB

    SECRET_KEY = "your-secret-key" 