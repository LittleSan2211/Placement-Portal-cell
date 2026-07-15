import os
from flask import Blueprint, request, jsonify , send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.sql import func
from datetime import datetime
from models import db, Student, JobPosition, Company, Application 
from task import export_applicants_csv_task 
from extension import cache


bp = Blueprint("company", __name__)

def make_company_cache_key(*args, **kwargs):
    try:
        user_id = get_jwt_identity()
        return f"{request.path}_company_user_{user_id}"
    except Exception:
        return request.path


@bp.route('/dashboard/metrics', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, make_cache_key=make_company_cache_key)
def getCompanyMetrics():
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Access denied"}), 403

    try:
        totalDrives = JobPosition.query.filter_by(company_id=company.id).count() or 0

        totalApplicants = db.session.query(func.count(Application.id))\
                        .join(JobPosition, Application.job_id == JobPosition.id)\
                        .filter(JobPosition.company_id == company.id).scalar() or 0
        
        shortlisted = db.session.query(func.count(Application.id))\
                      .join(JobPosition, Application.job_id == JobPosition.id)\
                      .filter(JobPosition.company_id == company.id)\
                      .filter(Application.status == "Shortlist").scalar() or 0
        
        selected_count = db.session.query(func.count(Application.id))\
                   .join(JobPosition, Application.job_id == JobPosition.id)\
                   .filter(JobPosition.company_id == company.id)\
                   .filter(Application.status == "Selected").scalar() or 0
        
        if totalApplicants > 0:
            successRate = round((selected_count / totalApplicants) * 100, 1)
        else:
            successRate = 0
        
        return jsonify({
            "totalDrives": totalDrives,
            "totalApplicants": totalApplicants,
            "shortlisted": shortlisted,
            "successRate": successRate 
        }), 200

    except Exception as e :
        return jsonify({
            "message": "Server side error.",
            "error": str(e)
        }), 500

        
@bp.route('/dashboard/latest-drives', methods=['GET'])
@jwt_required()
def getLatestDrives():
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Access denied"}), 403

    try:
        latest_job = JobPosition.query.filter_by(company_id = company.id)\
                     .order_by(JobPosition.id.desc()).limit(4).all()
        
        latest_drives_list = []
        for job in latest_job :
            apps_count = len(job.applications) if hasattr(job, 'applications') else 0
            latest_drives_list.append({
                "id": job.id,
                "title": job.title,
                "status": job.status,
                "deadline": job.application_deadline.strftime('%Y-%m-%d') if job.application_deadline else "N/A",
                "apps_count": apps_count
            })

        return jsonify(latest_drives_list), 200
    except Exception as e:
        return jsonify({"message": "Drives fetch error", "error": str(e)}), 500


@bp.route('/dashboard/role-analytics', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, make_cache_key=make_company_cache_key)
def getRoleAnalytics():
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Access denied"}), 403

    try:
        company_jobs = JobPosition.query.filter_by(company_id=company.id).all()
        role_analytics_list = []

        for job in company_jobs:
            total_apps = len(job.applications) if hasattr(job, 'applications') else 0
            selected_for_job = sum(1 for app in job.applications if app.status == 'Selected')
            shortlisted_for_job = sum(1 for app in job.applications if app.status == 'Shortlist')
            skills = job.skills_required if hasattr(job, 'skills_required') and job.skills_required else "N/A"
            
            role_analytics_list.append({
                "id": job.id,
                "role_name": job.title,
                "total_applicants": total_apps,
                "shortlisted": shortlisted_for_job,
                "selected": selected_for_job,
                "required_skills": skills,
                "status": job.status or "ONGOING"
            })

        return jsonify(role_analytics_list), 200
    except Exception as e:
        print("Crash in Analytics Table:", str(e))
        return jsonify({"message": "Analytics error", "error": str(e)}), 500
    

@bp.route('/dashboard/manage-drives', methods=['GET']) 
@jwt_required()
def manageDrives() :
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id = user_id).first()

    if not company:
        return jsonify({"message": "Access denied"}), 403

    try:
        all_jobs = JobPosition.query.filter_by(company_id = company.id).order_by(JobPosition.id.desc()).all()
        total_drives = len(all_jobs)
        ongoing_count = 0
        closed_count = 0 

        ongoing_drives_list = []
        all_drives_list = [] 

        for job in all_jobs :
            total_apps = len(job.applications) if hasattr(job, 'applications') else 0 

            if job.status == "ONGOING" :
                ongoing_count += 1 
                ongoing_drives_list.append({
                    "id" : job.id,
                    "title" : job.title,
                    "location": job.location or "Remote",
                    "deadline": job.application_deadline.strftime('%Y-%m-%d') if job.application_deadline else "N/A",
                    "status": job.status
                }) 
            else :
                closed_count += 1 
            
            all_drives_list.append({
                "id": job.id,
                "title": job.title,
                "package": job.salary or "N/A",
                "total_apps": total_apps,
                "status": job.status,
                "deadline": job.application_deadline.strftime('%Y-%m-%d') if job.application_deadline else "N/A"
            })

        return jsonify({
            "top_cards": {
                "totalDrives": total_drives,
                "ongoingDrives": ongoing_count,
                "closedDrives": closed_count
            },
            "ongoing_table": ongoing_drives_list,
            "all_drives_table": all_drives_list
        }), 200
    except Exception as e:
        print("Crash in Manage Drives Architecture:", str(e))
        return jsonify({"message": "Server side orchestration failed.", "error": str(e)}), 500
    

@bp.route('/dashboard/toggle-drive-status/<int:job_id>', methods=['POST'])
@jwt_required()
def toggleDriveStatus(job_id):
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id = user_id).first()

    if not company:
        return jsonify({"message": "Access denied"}), 403

    try: 
        job = JobPosition.query.filter_by(id=job_id, company_id = company.id).first()

        if not job :
            return jsonify({"message": "Job position not found"}), 404
        
        data = request.get_json()
        new_status = data.get("status")
        if new_status in ["ONGOING", "CLOSED"]:
            job.status = new_status
            db.session.commit()

            try:
                cache.clear() # Kyuki drive badli hai, poore student stream ka refresh hona zaroori hai
                print("Global cache cleared due to drive status modification.")
            except Exception as cache_err:
                print(f"Cache eviction failed: {cache_err}")

            return jsonify({"message": f"Drive status updated to {new_status} successfully."}), 200
        else:
            return jsonify({"message": "Invalid status value"}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Status shift failed.", "error": str(e)}), 500 


@bp.route('/dashboard/applicants/top-drives', methods=['GET'])
@jwt_required()
def getApplicantsV2():
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    
    if not company:
        return jsonify({"message": "Access denied"}), 403

    try:
        all_jobs = JobPosition.query.filter_by(company_id = company.id).all()

        drives_with_counts = []
        for job in all_jobs :
            total_apps = len(job.applications) if hasattr(job, 'applications') else 0
            drives_with_counts.append({
                "id": job.id,
                "title": job.title,
                "location": job.location or "Remote",
                "deadline": job.application_deadline.strftime('%Y-%m-%d') if job.application_deadline else "N/A",
                "status": job.status or "ONGOING",
                "apps_count": total_apps
            })

        top_4_drives = sorted(drives_with_counts, key=lambda x: x['apps_count'], reverse=True)[:4]
        return jsonify(top_4_drives), 200
    except Exception as e:
        print("Error in top-drives endpoint:", str(e))
        return jsonify({"message": "Error fetching top drives", "error": str(e)}), 500
    

@bp.route('/dashboard/applicants/drives-list', methods=['GET'])
@jwt_required()
def getApplicantsDrivesList(): 
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id = user_id).first()
    if not company :
        return jsonify({"message": "Access denied"}), 403
    
    try : 
        all_jobs = JobPosition.query.filter_by(company_id = company.id).all()

        drives_list = []
        for job in all_jobs :
            drives_list.append({
                "id": job.id,
                "title" : job.title
            })

        return jsonify(drives_list), 200 
    
    except Exception as e:
        print("Error in drives-list endpoint:", str(e))
        return jsonify({"message": "Error fetching drives list", "error": str(e)}), 500
    

@bp.route('/dashboard/applicants/table', methods=['GET'])
@jwt_required()
def getApplicantsTableData():
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Access denied"}), 403

    try: 
        job_id = request.args.get("job_id", type=int)

        if not job_id:
            return jsonify({"message": "Please select a drive first to view roster."}), 200 
        
        applications = Application.query.join(JobPosition).filter(
            Application.job_id == job_id,JobPosition.company_id == company.id ).all() 
        
        applicants_table = []
        for app in applications : 
            student = Student.query.filter_by(id = app.student_id).first()
            if student:
                applicants_table.append({
                    "application_id": app.id,
                    "student_name": student.full_name,
                    "branch": student.branch,
                    "status": app.status or "PENDING"
                })
                
        return jsonify(applicants_table), 200
        
    except Exception as e:
        print("Error in applicants table endpoint:", str(e))
        return jsonify({"message": "Error compiling table matrix", "error": str(e)}), 500


@bp.route('/dashboard/applicants/student-profile/<int:app_id>', methods=['GET'])
@jwt_required()
def getStudentProfileDetails(app_id):
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Access denied"}), 403

    try: 
        app = Application.query.join(JobPosition).filter(
            Application.id == app_id ,
            JobPosition.company_id == company.id
        ).first()

        if not app :
            return jsonify({"message": "Profile context missing or unauthorized"}), 404
        
        student = Student.query.filter_by(id=app.student_id).first()
        if not student :
            return jsonify({"message": "Student record not found"}), 404
        
        interview_time_str = ""
        if hasattr(app, 'interview_date') and app.interview_date is not None:
            interview_time_str = app.interview_date.strftime('%Y-%m-%dT%H:%M')
        
        return jsonify({
            "application_id": app.id,
            "student_id": student.id,
            "student_name": student.full_name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "skills": student.skills or "N/A",
            "status": app.status or "PENDING",
            "feedback": app.feedback or "",
            "interview_time": interview_time_str,
            "resume_url": f"http://localhost:5000/student/uploads/resumes/{os.path.basename(student.resume_path.replace('\\', '/'))}" if student.resume_path else None
        }), 200

    except Exception as e:
        print("Error in student-profile endpoint:", str(e))
        return jsonify({"message": "Error loading profile details", "error": str(e)}), 500


@bp.route('/dashboard/applicants/update-workflow', methods=['POST'])
@jwt_required()
def updateApplicantWorkflow():
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Access denied"}), 403

    try:
        data = request.get_json()
        app_id = data.get("application_id")
        target_status = data.get("status")
        feedback_text = data.get("feedback")
        interview_time_str = data.get("interview_time")

        if not app_id or not target_status:
            return jsonify({"message": "Missing application_id or status."}), 400

        application = Application.query.join(JobPosition).filter(
            Application.id == app_id,
            JobPosition.company_id == company.id
        ).first()

        if not application:
            return jsonify({"message": "Application record not found or unauthorized"}), 404
        
        application.status = target_status
        application.feedback = feedback_text
        
        # 🔥 CRITICAL SYNC: Using real 'interview_date' database schema column
        if target_status == "Shortlist" and interview_time_str:
            try:
                application.interview_date = datetime.strptime(interview_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                return jsonify({"message": "Invalid date-time format. Use YYYY-MM-DDTHH:MM"}), 400
        else:
            if hasattr(application, 'interview_date'):
                application.interview_date = None

        if target_status == "Selected":
            job = JobPosition.query.filter_by(id=application.job_id).first()
            

            from models import Placement 
            existing_placement = Placement.query.filter_by(
                student_id=application.student_id, 
                job_id=application.job_id
            ).first()
            
            if not existing_placement:
                new_placement_record = Placement(
                    student_id=application.student_id,
                    job_id=application.job_id,
                    
                    company_id=company.id if hasattr(Placement, 'company_id') else None,
                    package=job.salary if job and hasattr(job, 'salary') else 0.0,
                    status="PLACED",
                    placed_at=datetime.utcnow()
                )
                db.session.add(new_placement_record)

        db.session.commit()
        try:
            cache.delete(f'view//company/dashboard/metrics_company_user_{user_id}')
            cache.delete(f'view//company/dashboard/role-analytics_company_user_{user_id}')

            if application and application.student:
                student_user_id = application.student.user_id
                cache.delete(f'view//student/dashboard/explore-jobs_user_{student_user_id}')
                
            print("Global cache cleared due to drive status modification.")

        except Exception as cache_err:
            print(f"Cache eviction failed: {cache_err}")

        return jsonify({"message": "Applicant pipeline synchronized successfully."}), 200
    except Exception as e:
        db.session.rollback()
        print("Crash in update workflow endpoint:", str(e))
        return jsonify({"message": "Workflow update failed", "error": str(e)}), 500
    

@bp.route('/dashboard/applicants/trigger-export', methods=['POST'])
@jwt_required()
def trigger_export():
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Unauthorized"}), 403

    task = export_applicants_csv_task.delay(company.id)
    
    return jsonify({
        "message": "Batch export job successfully queued using Redis Broker!",
        "task_id": task.id,
        "download_url": f"/company/dashboard/applicants/download-report/company_{company.id}_applicants.csv"
    }), 202

from secret import PROJECT_ROOT

@bp.route('/dashboard/applicants/download-report/<filename>', methods=['GET'])
def download_export_file(filename):
    directory = os.path.join(PROJECT_ROOT,"backend", 'static', 'exports')
    return send_from_directory(directory, filename, as_attachment=True)


@bp.route('/dashboard/create-new-drive', methods=['POST'])
@jwt_required()
def createNewDrive():
    user_id = get_jwt_identity()
    company = Company.query.filter_by(user_id=user_id).first()
    
    if not company:
        return jsonify({"message": "Access denied"}), 403

    try:
        data = request.get_json()
        title = data.get("title")
        salary = data.get("salary")
        location = data.get("location")
        deadline_str = data.get("deadline")
        skills = data.get("skills")

        if not title or not salary or not location or not deadline_str:
            return jsonify({"message": "Sari fields bharna compulsory hai!"}), 400

        # Parse string date into database format
        deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d')

        new_job = JobPosition(
            company_id=company.id,
            title=title,
            salary=salary,
            location=location,
            application_deadline=deadline_date,
            skills_required=skills,
            status="ONGOING"  # default dynamic start
        )

        db.session.add(new_job)
        db.session.commit()

        # Evict cache matrix for analytics updates
        try:
            cache.clear()
            print("[Cache] Company metrics cleared for new drive orchestration.")
        except Exception as e:
            print(f"Cache clear failure: {e}")

        return jsonify({"message": "Placement drive successfully launched live!"}), 201

    except Exception as e:
        db.session.rollback()
        print("Crash inside createNewDrive routing:", str(e))
        return jsonify({"message": "Internal process collapsed.", "error": str(e)}), 500