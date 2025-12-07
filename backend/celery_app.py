from celery import Celery
from flask import Flask
from config import Config
from extensions import db,mail,cache

def create_celery(app):
    celery_app = Celery(
        app.import_name, 
        broker=app.config['CELERY_BROKER_URL'], 
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery_app.conf.update(app.config)
    
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)
    
    celery_app.Task = ContextTask
    return celery_app

flask_app = Flask('quiz_app') 
flask_app.config.from_object(Config)

db.init_app(flask_app)
mail.init_app(flask_app)
cache.init_app(flask_app)

celery = create_celery(flask_app) 
celery.conf.update(CELERY_IMPORTS=('tasks',))