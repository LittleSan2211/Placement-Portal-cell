from flask_caching import Cache
from flask_mail import Mail
from celery import Celery

cache = Cache()
mail = Mail()

celery = Celery(__name__) 