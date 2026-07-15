# ------------------------------ Step 1 : Import Libraries ------------------------------------------- 
import os 
import sys
from flask import Flask
from flask_jwt_extended import JWTManager 
from datetime import timedelta
from flask_cors import CORS 
from celery.schedules import crontab 
from secret import password
from extension import cache, mail , celery

# Global Flask App Core Instantiation
base_dir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(base_dir, 'instance')
app = Flask(__name__,instance_path=instance_dir)


# Core Application Configurations
app.config['SECRET_KEY'] = 'SP_19116141' 
canonical_db_path = os.path.join(instance_dir, 'placement.db')

try:
    os.makedirs(os.path.dirname(canonical_db_path), exist_ok=True)
except OSError:
    pass
    
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{canonical_db_path.replace('\\\\', '/')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'My_19116141'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '24f2007883'  
app.config['MAIL_PASSWORD'] = password      
app.config['MAIL_DEFAULT_SENDER'] = '24f2007883@gmail.com'

cache_config = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 0,
    'CACHE_DEFAULT_TIMEOUT': 300 
}
app.config.from_mapping(cache_config)

# Extensions Initialization
mail.init_app(app)
cache.init_app(app)
CORS(app, supports_credentials=True, origins=["http://localhost:8080"])
jwt = JWTManager(app)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Celery Base Initialization
celery.main = __name__
celery.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    timezone='UTC',
    enable_utc=True,
    include=['task'], # Tasks ko link rakhega,
    worker_hijack_root_logger=False
)

# Celery Beat Automated Schedules
celery.conf.beat_schedule = {
    'send-interview-reminders-1-day-before': {
        'task': 'task.send_interview_reminders_task',
        'schedule': crontab(hour=9, minute=0),    # 'schedule': 10.0,  # Iska matlab har 10 seconds me automatic run hoga
    },
    'execute-monthly-corporate-analytics-report': {
        'task': 'task.generate_monthly_placement_reports',
        'schedule': timedelta(seconds=15),   # $$\text{crontab(minute, hour, day\_of\_month, month\_of\_year, day\_of\_week)}$$
    },
}

class ContextTask(celery.Task):
    abstract = True
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)
celery.Task = ContextTask

# --------------------------- Step 2 : Database Context & Seeding -------------------------------------
from models import db, User, Company, Student, JobPosition, Application, Placement
from sqlalchemy import inspect
from sqlalchemy.orm import load_only
from data import APPLICATIONS_DATA, COMPANIES_DATA, JOBS_DATA, PLACEMENTS_DATA, STUDENTS_DATA

db.init_app(app)

with app.app_context():
    db.create_all()

    # Mock data seeding logic
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', email='admin@gmail.com', role='Admin', is_approved=True)
        admin_user.set_password('admin')
        db.session.add(admin_user)
        db.session.commit()

    inspector = inspect(db.engine)
    company_columns = [col['name'] for col in inspector.get_columns('company')] if 'company' in inspector.get_table_names() else []
    has_company_about = 'about' in company_columns

    for company_data in COMPANIES_DATA:
        username = company_data["username"]
        email = f"{username}@gmail.com"
        company_user = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
        company_exists = Company.query.options(load_only(Company.id, Company.company_name)).filter_by(company_name=company_data["company_name"]).first()

        if company_exists and has_company_about:
            company_exists.about = company_data["about"]

        if not company_exists:
            if not company_user:
                company_user = User(username=username, email=email, role='Company', is_approved=True)
                company_user.set_password(f"{username}@1234")
                db.session.add(company_user)
                db.session.flush()

            if Company.query.filter_by(user_id=company_user.id).first():
                continue

            new_company_kwargs = dict(
                user_id=company_user.id,
                company_name=company_data["company_name"],
                industry=company_data["industry"],
                location=company_data["location"],
                website=company_data["website"],
                hr_name=company_data["hr_name"],
                hr_email=email,
                approval_status="APPROVED"
            )
            if has_company_about:
                new_company_kwargs['about'] = company_data["about"]

            new_company = Company(**new_company_kwargs)
            db.session.add(new_company)
    db.session.commit()

    for job_data in JOBS_DATA:
        company = Company.query.filter_by(company_name=job_data["company_name"]).first()
        job = JobPosition.query.filter_by(title=job_data["title"], company_id=company.id).first() if company else None
        if company and not job:
            new_job = JobPosition(
                company_id=company.id, job_type=job_data["job_type"], title=job_data["title"],
                description=job_data["description"], benefits=job_data["benefits"], salary=job_data["salary"],
                skills_required=job_data["skills_required"], eligible_branch=job_data["eligible_branch"],
                eligible_year=job_data["eligible_year"], cgpa=job_data["cgpa"], location=job_data["location"],
                approval_status=job_data["approval_status"], status=job_data["status"]
            )
            db.session.add(new_job)
    db.session.commit()

    for student_data in STUDENTS_DATA:
        username = student_data["username"]
        email = f"{username}@gmail.com"
        student_user = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
        if not student_user:
            student_user = User(username=username, email=email, role='Student', is_approved=True)
            student_user.set_password(f"{username}@1234")
            db.session.add(student_user)
            db.session.flush()

        student = Student.query.filter_by(user_id=student_user.id).first()
        if not student:
            new_student = Student(
                user_id=student_user.id, full_name=student_data["full_name"], contact=student_data["contact"],
                about=student_data["about"], branch=student_data["branch"], year=student_data["year"],
                cgpa=student_data["cgpa"], skills=student_data["skills"], experience=student_data["experience"],
                resume_path=student_data["resume_path"]
            )
            db.session.add(new_student)
    db.session.commit()

    for application_data in APPLICATIONS_DATA:
        student_user = User.query.filter_by(username=application_data["student_username"]).first()
        company = Company.query.filter_by(company_name=application_data["company_name"]).first()
        job = JobPosition.query.filter_by(title=application_data["job_title"], company_id=company.id).first() if company else None
        student = Student.query.filter_by(user_id=student_user.id).first() if student_user else None
        application = Application.query.filter_by(student_id=student.id, job_id=job.id).first() if student and job else None

        if student and job and not application:
            new_application = Application(student_id=student.id, job_id=job.id, status=application_data["status"], feedback=application_data["feedback"])
            db.session.add(new_application)
    db.session.commit()

    print("Mock data seeded successfully!")

# --------------------------- Step 3 : Route Blueprints Registration -------------------------------------


from routes.auth import bp as auth_bp
from routes.student import bp as student_bp
from routes.company import bp as company_bp
from routes.admin import bp as admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(company_bp, url_prefix='/company')

if __name__ == '__main__':
    app.run(debug=True)




# celery -A run.celery worker --loglevel=info -P solo 
# celery -A run.celery beat --loglevel=info