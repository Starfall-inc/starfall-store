from app import create_app
from app.extensions import db  # Import db
from flask_migrate import Migrate  # Import Migrate

app = create_app()
migrate = Migrate(app, db)  # Initialize Migrate
