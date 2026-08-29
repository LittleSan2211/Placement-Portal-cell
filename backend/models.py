from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash , check_password_hash

def get_default_deadline():
    return datetime.now() + timedelta(days=30)

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120),nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False)

    def set_password(self, password1):
        self.password = generate_password_hash(password1)

    def check_password(self, password1):
        return check_password_hash(self.password, password1)


# ================================= Table 2 ========================================
class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id') ,nullable=False, unique = True)
    company_name = db.Column(db.String(120),nullable=False)
    about = db.Column(db.String)
    industry = db.Column(db.String(120),nullable=False)
    location = db.Column(db.String(120),nullable=False)
    website = db.Column(db.String(120),unique=True,nullable=False)
    hr_name = db.Column(db.String(120),nullable=False)
    hr_email = db.Column(db.String(120),unique=True,nullable=False)
    approval_status = db.Column(db.String(120),nullable=False, default="PENDING")                         #PENDING | APPROVED | REJECTED
    is_blacklist = db.Column(db.Boolean,nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    company = db.relationship("User", backref="company")


# ==================================== Table 3 ==========================================
class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer , primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id') ,nullable=False,unique = True)
    full_name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    about = db.Column(db.String)
    branch = db.Column(db.String(120))
    year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    skills = db.Column(db.String)
    experience = db.Column(db.Text, nullable=True)
    resume_path = db.Column(db.String)
    is_blacklist = db.Column(db.Boolean,nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    student = db.relationship("User",backref="student")
 

# ====================================== Table 4 ==========================================
class JobPosition(db.Model):
    __tablename__ = 'jobposition'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"),nullable=False)
    job_type = db.Column(db.String, nullable=False, default="Internship")             # Full Time | Internship
    title = db.Column(db.String)
    description = db.Column(db.String)
    benefits = db.Column(db.String)
    salary = db.Column(db.Integer)
    skills_required = db.Column(db.String)
    eligible_branch = db.Column(db.String(120))
    eligible_year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    location = db.Column(db.String(120), nullable=False, default='Delhi')
    application_deadline = db.Column(db.DateTime, default= get_default_deadline )
    approval_status = db.Column(db.String(120), default="APPROVED")                               # PENDING | APPROVED | CLOSED
    status = db.Column(db.String,nullable=False, default='ONGOING')                              # On Going | CLOSED
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    company = db.relationship("Company",backref="jobs")


# ==================================== Table 5 ============================================
class Application(db.Model):
    __tablename__  = "application"
    id = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    job_id = db.Column(db.Integer,db.ForeignKey("jobposition.id"), nullable=False)
    application_date = db.Column(db.DateTime,server_default=func.now())
    status = db.Column(db.String,nullable=False, default = "Pending")                                  # Selected | Reject | Shortlist | Pending
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    applied_at = db.Column(db.DateTime, server_default=func.now()) 
    feedback = db.Column(db.Text, nullable=True)
    interview_date = db.Column(db.DateTime)
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='uq_student_job'),
    )
    student = db.relationship("Student",backref="applications")
    job = db.relationship("JobPosition",backref="applications")

#==================================== Table 6 ================================================
class Placement(db.Model):
    __tablename__ = "placement"
    id = db.Column(db.Integer,primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"), nullable=False, unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"),  nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    job_id = db.Column(db.Integer,db.ForeignKey("jobposition.id"))
    salary = db.Column(db.Integer)
    offer_letter_path = db.Column(db.String(255), nullable=True) 
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    application = db.relationship("Application", backref=db.backref("placement", uselist=False))
    student = db.relationship("Student",backref="placement_info")
    company = db.relationship("Company",backref="placed_students")
    job = db.relationship("JobPosition", backref="placement_job")



