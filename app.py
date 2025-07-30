from flask import Flask
from controllers.user_controller import user_bp   # Import user blueprint
from controllers.admin_controller import admin_bp # Import admin blueprint
from models.database import db # Importing the database
from flask_migrate import Migrate
app = None
def create_app():
    app = Flask(__name__) # Create a new Flask application
    app.secret_key = "ans1234"
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp) 
    app.debug=True # Enable debug mode for development
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///vehicle_parking.sqlite3" #database
    db.init_app(app) # Initialize the database with the Flask app
    migrate = Migrate(app, db)
    app.app_context().push() # Brings everything under context of flask application
    return app
 # Import all models
app = create_app()
from models.model import *
db.create_all()
if __name__=="__main__":
    app.run()