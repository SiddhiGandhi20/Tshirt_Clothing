from flask import Flask
from flask_pymongo import PyMongo
from config import Config
from flask_cors import CORS
from utils import JSONEncoder
import os

from routes.user_signup_routes import create_auth_routes
from routes.user_login_routes import setup_login_routes
from routes.product_routes import create_product_routes
from routes.tshirt_routes import create_tshirts_routes
from routes.hoodies_routes import create_hoodies_routes
from routes.combos_routes import create_combos_routes
from routes.admin_login_routes import setup_admin_routes


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

mongo = PyMongo(app)

# Set custom JSON encoder to handle MongoDB ObjectId
app.json_encoder = JSONEncoder

# Register authentication routes (signup)
auth_bp = create_auth_routes(mongo.db)
app.register_blueprint(auth_bp, url_prefix="/auth")

# Register login routes (login)
login_bp = setup_login_routes(mongo.db)
app.register_blueprint(login_bp, url_prefix="/login")  # Fix: changed /auth to /login

# Register product routes
app.register_blueprint(create_product_routes(mongo.db, app.config['UPLOAD_FOLDER']), url_prefix="/api")

app.register_blueprint(create_tshirts_routes(mongo.db, app.config['UPLOAD_FOLDER']))

app.register_blueprint(create_hoodies_routes(mongo.db, app.config['UPLOAD_FOLDER']))
app.register_blueprint(create_combos_routes(mongo.db, app.config['UPLOAD_FOLDER']))

app.register_blueprint(setup_admin_routes(mongo.db))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # Ensure the port is specified
