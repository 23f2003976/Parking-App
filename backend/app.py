from flask import Flask
from flask_cors import CORS
from config import Config
from werkzeug.security import generate_password_hash
from extensions import db, cache, mail
from celery_app import create_celery
from models import User
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp
# from tasks import schedule_monthly_reports, send_daily_reminders

celery = None 
def create_app():
    global celery
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"], "supports_credentials": True}})

    db.init_app(app)
    cache.init_app(app)
    mail.init_app(app)

    celery = create_celery(app)
    
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
        if not admin:
            admin = User(
                username=app.config['ADMIN_USERNAME'],
                password=generate_password_hash(app.config['ADMIN_PASSWORD']),
                full_name='Parking Admin',
                role='admin',
                email='admin@parkingapp.com'
            )
            db.session.add(admin)
            db.session.commit()

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')

    return app

# send_daily_reminders.delay()
# schedule_monthly_reports.delay()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)
