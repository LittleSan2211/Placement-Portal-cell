import os
from flask import request, jsonify, Blueprint, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from models import JobPosition, Student, db, Application
from extension import cache

bp = Blueprint('student', __name__)
 
def make_user_cache_key(*args, **kwargs):
    try:
        user_id = get_jwt_identity()
        return f"{request.path}_user_{user_id}"
    except Exception:
        return request.path

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def get_resume_storage_dir():
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'resumes'))
    try:
        os.makedirs(upload_dir, exist_ok=True)
    except Exception as e:
        print(f"DIRECTORY CREATION FAILED AT PATH: {upload_dir}. Error: {e}")
    return upload_dir


def build_resume_url(resume_path):
    if not resume_path:
        return None

    filename = os.path.basename(resume_path.replace('\\', '/'))
    if not filename:
        return None

    return f"http://localhost:5000/student/uploads/resumes/{filename}"


@bp.route('/uploads/resumes/<path:filename>')
def global_serve_resume(filename):
    upload_path = get_resume_storage_dir()
    return send_from_directory(upload_path, filename, as_attachment=False, mimetype='application/pdf')

@bp.route('/dashboard/identity', methods=['GET'])
@jwt_required()
def getStudentIdentity():
    user_id = get_jwt_identity()
    
    try:
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({"message": "Student profile data missing"}), 404
            
        return jsonify({
            "full_name": student.full_name,
            "branch": student.branch
        }), 200
        
    except Exception as e:
        print("Crash in Student identity endpoint:", str(e))
        return jsonify({"message": "Error loading identity data", "error": str(e)}), 500
    
@bp.route('/dashboard/top-metrics', methods=['GET'])
@jwt_required()
def getStudentMetrics():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    if not student :
        return jsonify({"message": "Student profile not linked"}), 404 
    
    try : 
        total_applied = Application.query.filter_by(student_id = student.id).count() or 0 

        shortlisted = Application.query.filter_by(
            student_id = student.id, status="Shortlist").count() or 0 
        
        offers_received = Application.query.filter_by(
            student_id = student.id, status="Selected").count() or 0 
        
        return jsonify({
            "applied": total_applied,
            "shortlisted": shortlisted,
            "offers": offers_received
        }), 200

    except Exception as e:
        print("Error in top metrics:", str(e))
        return jsonify({"message": "Server error loading metrics", "error": str(e)}), 500


@bp.route('/dashboard/high-packages', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, make_cache_key=make_user_cache_key)
def gethighPackages() :
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    if not student :
        return jsonify({"message": "Student profile not linked"}), 400 
    
    try:
        high_packages_query = JobPosition.query.filter_by(status="ONGOING")\
                              .group_by(JobPosition.company_id)\
                              .order_by(JobPosition.salary.desc())\
                              .limit(4)
        
        high_packages_list = [{
            "company_name": job.company.company_name if job.company else "Elite Venture",
            "role_title": job.title,
            "package_lpa": job.salary,
            "location": job.location or "Pan India"
        } for job in high_packages_query]

        return jsonify(high_packages_list), 200

    except Exception as e:
        print("Error in high packages fetch:", str(e))
        return jsonify({"message": "Server error loading high packages", "error": str(e)}), 500
    
@bp.route('/dashboard/market-trends', methods=['GET'])
@jwt_required()
@cache.cached(timeout=600,make_cache_key=make_user_cache_key)
def getMarketTrends():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    if not student :
        return jsonify({"message": "Student profile not linked"}), 400 
    
    try: 
        trending_roles_raw = db.session.query(
            JobPosition.title, 
            func.count(JobPosition.id).label("total_companies"),
            func.avg(JobPosition.salary).label("avg_package")
        ).filter(JobPosition.status == "ONGOING")\
        .group_by(JobPosition.title)\
        .order_by(func.count(JobPosition.id).desc())\
        .limit(20).all() 

        trending_roles_matrix = [{
            "role": row.title,
            "total_companies": row.total_companies,
            "avg_package": round(float(row.avg_package), 2)
        } for row in trending_roles_raw]

        skill_pool = db.session.query(JobPosition.skills_required)\
                     .filter(JobPosition.status == "ONGOING").all()
        
        unique_skills = set() 
        for row in skill_pool :
            if row.skills_required :
                # Comma separated string ko saaf karke unique set me add karenge
                tokens = [s.strip() for s in row.skills_required.split(",") if s.strip()]
                unique_skills.update(tokens)

        trending_skills_list = list(unique_skills)[:10] 
        return jsonify({
            "trending_roles": trending_roles_matrix,
            "trending_skills": trending_skills_list
        }), 200

    except Exception as e:
        print("Error loading market trends:", str(e))
        return jsonify({"message": "Server error loading trends matrix", "error": str(e)}), 500

@bp.route('/dashboard/explore-jobs', methods=['GET'])
@jwt_required()
@cache.cached(timeout=120, query_string=True, make_cache_key=make_user_cache_key)
def exploreJobsFeed():
    user_id = get_jwt_identity()
    # 1. Student ka record fetch karo
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({"message": "Student profile not linked"}), 404
    
    try:
        jobs_with_status = db.session.query(
                JobPosition,
                Application.status.label("app_status"), 
                Application.applied_at.label("applied_time") 
                ).outerjoin(Application, db.and_(
                    Application.student_id == student.id,
                    Application.job_id == JobPosition.id
                )).filter(JobPosition.status == "ONGOING", JobPosition.approval_status == "APPROVED")\
                .order_by(JobPosition.created_at.desc()).all() 
        
        explore_feed = []
        for job, app_status, applied_time in jobs_with_status:
            explore_feed.append({
                "job_id": job.id,
                "company_name": job.company.company_name if job.company else "Tech Venture",
                "company_about": job.company.about if job.company else "No description available.",
                "title": job.title,
                "job_type": job.job_type or "Full Time",
                "salary": job.salary,
                "location": job.location, # 'Remote' ya 'Location (In-Site)' 
                "skills_required": job.skills_required or "",
                "benefits": job.benefits or "Standard corporate perks",
                "eligible_branch": job.eligible_branch or "All",
                "eligible_year": job.eligible_year,
                "cgpa_required": job.cgpa or 0.0,
                "deadline": job.application_deadline.strftime("%d %b %Y") if job.application_deadline else "N/A",
                

                "applied_status": app_status if app_status else "NOT_APPLIED",
                "applied_at_date": applied_time.strftime("%d %b %Y") if applied_time else None,
                "is_student_eligible": (student.cgpa >= (job.cgpa or 0.0))
            })

        return jsonify(explore_feed), 200

    except Exception as e:
        print("Crash in explore jobs backend:", str(e))
        return jsonify({"message": "Failed to load job stream", "error": str(e)}), 500
         

@bp.route('/apply', methods=['POST'])  
@jwt_required()
def applyToPlacementDrive():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({"message": "Student directory node missing."}), 404
        
    data = request.get_json() or {}
    job_id = data.get('job_id')
    
    if not job_id:
        return jsonify({"message": "Missing required job parameter allocation."}), 400
        
    try:
        job = JobPosition.query.filter_by(id=job_id, status="ONGOING").first()
        if not job:
            return jsonify({"message": "This job opening has been archived or closed."}), 404
            
        existing_app = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
        if existing_app:
            return jsonify({"message": "Logs indicate you have already applied for this drive profile."}), 400
            
        if not student.resume_path:
            return jsonify({"message": "Please configure and upload your Resume on 'My Profile' first."}), 400
            
        if student.cgpa < (job.cgpa or 0.0):
            return jsonify({"message": "Application aborted: CGPA does not satisfy recruiters criteria."}), 400
            

        new_application = Application(
            student_id=student.id,
            job_id=job.id,
            status="Pending", 
            feedback="Your application parameters are currently under recruitment review desk."
        )
        
        db.session.add(new_application)
        db.session.commit()
        try:
            cache.delete(f'view//student/dashboard/explore-jobs_user_{user_id}')
            print(f"Redis Cache evicted for user_{user_id} after successful application!")
        except Exception as cache_err:
            print(f"Cache eviction failed: {cache_err}")
        
        return jsonify({"message": "Application logged and transmitted to recruiter hub successfully!"}), 200
        
    except Exception as e:
        db.session.rollback()
        print("Crash in drive submission process:", str(e))
        return jsonify({"message": "Internal compilation error logging drive data.", "error": str(e)}), 500


# ==================================================================
# ROUTE: STUDENT APPLIED HISTORY STREAM (CLEAN & LIGHTWEIGHT)
# ==================================================================
@bp.route('/dashboard/applied-history', methods=['GET'])
@jwt_required()
def getAppliedHistory():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({"message": "Student profile not linked"}), 404
        
    try:
        # Simple Inner Join between Application and JobPosition
        applied_drives = db.session.query(Application, JobPosition)\
            .join(JobPosition, Application.job_id == JobPosition.id)\
            .filter(Application.student_id == student.id)\
            .order_by(Application.applied_at.desc()).all()

        history_feed = []
        offers_count = 0  # Counter for total offers confirmed
        
        for app, job in applied_drives:
            if app.status == "Selected":
                offers_count += 1
                
            history_feed.append({
                "application_id": app.id,
                "job_id": job.id,
                "company_name": job.company.company_name if job.company else "Elite Venture",
                "title": job.title,
                "salary": job.salary,
                "location": job.location,
                "job_type": job.job_type,
                
                # Tracking parameters
                "status": app.status, # Selected | Reject | Shortlist | Pending
                "feedback": app.feedback or "Your application parameters are currently under recruitment review desk.",
                "interview_date": app.interview_date.strftime("%d %b %Y at %I:%M %p") if app.interview_date else None,
                "applied_at_date": app.applied_at.strftime("%d %b %Y") if app.applied_at else "N/A"
            })

        return jsonify({
            "total_offers": offers_count,
            "total_applied": len(history_feed),
            "history": history_feed
        }), 200

    except Exception as e:
        print("Crash in applied history endpoint:", str(e))
        return jsonify({"message": "Failed to compile recruitment logs", "error": str(e)}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_student_profile():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({"message": "Student profile shell not found."}), 404
        
    return jsonify({
        "full_name": student.full_name,
        "contact": student.contact,
        "about": student.about,
        "branch": student.branch,
        "year": student.year,
        "cgpa": student.cgpa,
        "skills": student.skills,
        "experience": student.experience,
        "resume_path": student.resume_path
    }), 200

@bp.route('/profile/update', methods=['POST'])
@jwt_required()
def update_profile():
    try: # 🔥 BADA FIX: Sabse pehli line se try block lagao!
        user_id = get_jwt_identity()
        
        # Agar DB crash yahan hua, toh ab except block usko log karega
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({"message": "Student profile shell not linked."}), 404

        form_data = request.form.to_dict(flat=True)

        f_name = form_data.get('full_name')
        if f_name and str(f_name).strip().lower() not in ['null', 'undefined', '']:
            student.full_name = str(f_name).strip()

        contact_val = form_data.get('contact')
        if contact_val and str(contact_val).strip().lower() not in ['null', 'undefined', '']:
            student.contact = str(contact_val).strip()[:15]

        if 'about' in form_data:
            student.about = form_data.get('about') or None
        if 'branch' in form_data:
            student.branch = form_data.get('branch') or None
        if 'skills' in form_data:
            student.skills = form_data.get('skills') or None
        if 'experience' in form_data:
            student.experience = form_data.get('experience') or None

        year_val = form_data.get('year')
        if year_val and str(year_val).strip().lower() not in ['null', 'undefined', '']:
            try:
                student.year = int(float(year_val))
            except (TypeError, ValueError):
                pass

        cgpa_val = form_data.get('cgpa')
        if cgpa_val and str(cgpa_val).strip().lower() not in ['null', 'undefined', '']:
            try:
                student.cgpa = float(cgpa_val)
            except (TypeError, ValueError):
                pass

        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename:
                if not allowed_file(file.filename):
                    return jsonify({"message": "Only PDF resumes are allowed."}), 400
                try:
                    storage_dir = get_resume_storage_dir()
                    filename = secure_filename(f"stu_{student.id}_{file.filename}")
                    file_path = os.path.join(storage_dir, filename)
                    print(f"ATTEMPTING TO SAVE RESUME FILE TO DISK: {file_path}")
                    file.save(file_path)
                    student.resume_path = f"static/uploads/resumes/{filename}"
                    print("FILE WRITE SUCCESSFUL!")
                except Exception as file_io_err:
                    print(f"RESUME FILE SAVE FAILED: {file_io_err}")
                    return jsonify({"message": "Resume upload failed.", "error": str(file_io_err)}), 500

        db.session.commit()
        try:
            cache.delete(f'view//student/dashboard/explore-jobs_user_{user_id}')
            print(f"Redis Cache evicted for user_{user_id} after successful application!")
        except Exception as cache_err:
            print(f"Cache eviction failed: {cache_err}")

        return jsonify({
            "message": "Profile configuration tokens parsed successfully!",
            "resume_url": build_resume_url(student.resume_path)
        }), 200

    except Exception as db_matrix_error:
        db.session.rollback()
        
        return jsonify({"message": "Database transaction constraints violation", "error": str(db_matrix_error)}), 500