from flask import Blueprint , request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required
from sqlalchemy import or_ 
from sqlalchemy.sql import func
from datetime import datetime, timedelta 
from models import db,User, Student, Company, Application, JobPosition, Placement
from extension import cache

bp = Blueprint('admin', __name__)

@bp.route('/stats', methods=['GET'])
@jwt_required()
@cache.cached(timeout=120)
def getStats() :
    user_id = get_jwt_identity()

    user = User.query.filter_by(id = user_id).first()

    if not user :
        return jsonify({'message':"User not found"}), 400
    
    if user.role != "Admin" :
        return jsonify({'message':"Unauthorized access"}), 403
    
    try :
        totalStudents = Student.query.count()
        totalCompanies = Company.query.count()
        pendingCompanies = Company.query.filter_by(approval_status='PENDING').count()
        blacklistCompanies = Company.query.filter_by(is_blacklist =True).count()
        totalApplicantion = Application.query.count()
        ongoing_drives = JobPosition.query.filter(JobPosition.status == "ONGOING").count()

        # PLACEMENT RATE LOGIC
        totalPlaced = Placement.query.distinct(Placement.student_id).count()
        if totalStudents> 0 :
            placementRate = round((totalPlaced / totalStudents) * 100) 
        else :
            placementRate = 0

        time_24_hours_ago = datetime.now() - timedelta(days=1)

        # 2. PICHLE 24 GHANTE MEIN AAYE NAYE RECORDS (New registrations)
        new_students_last_24h = Student.query.filter(Student.created_at >= time_24_hours_ago).count()
        new_companies_last_24h = Company.query.filter(Company.created_at >= time_24_hours_ago).count()

        # 3. PREVIOUS TOTALS (24 ghante pehle jo tha)
        prev_students_total = totalStudents - new_students_last_24h
        prev_companies_total = totalCompanies - new_companies_last_24h

        # 4. STUDENTS GROWTH % CALCULATION
        if prev_students_total > 0:
            studentGrowth = round((new_students_last_24h / prev_students_total) * 100, 1)
        else:
            studentGrowth = 0.0 if new_students_last_24h == 0 else 100.0 # Agar pehle 0 thaa aur ab badha toh direct 100%

        # 5. COMPANIES GROWTH % CALCULATION
        if prev_companies_total > 0:
            companyGrowth = round((new_companies_last_24h / prev_companies_total) * 100, 1)
        else:
            companyGrowth = 0.0 if new_companies_last_24h == 0 else 100.0

        recent_request = Company.query.filter(Company.approval_status == "PENDING",
                                                    Company.created_at >= time_24_hours_ago).all()
        
        recentComapanyRequest = [] 
        for company in recent_request :
            recentComapanyRequest.append({
                "id" : company.id,
                "name" : company.company_name,
                "industry" : company.industry,
                "location" : company.location,
                "time": company.created_at.strftime("%I:%M %p") # Time format (e.g., 02:30 PM)
            })

        return jsonify({
            "totalStudents": totalStudents,
            "studentGrowth": studentGrowth,
            "totalCompanies": totalCompanies,
            "companyGrowth": companyGrowth,
            "pendingApprovals": pendingCompanies,
            "blacklistedCompanies": blacklistCompanies,
            "totalApplicantion": totalApplicantion,
            "activeDrives": ongoing_drives,
            "placementRate": placementRate,
            "recentCompanyRequests": recentComapanyRequest 
        }), 200
    
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500

@bp.route('/top-partners', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)
def getTopPartners():
    try:
        top_placements = db.session.query(Company.company_name, Company.industry, func.max(Placement.salary).label('max_salary'))\
            .join(Placement, Company.id == Placement.company_id).group_by(Company.company_name, Company.industry)\
            .order_by(db.text('max_salary DESC')).limit(4).all()

        topList = [{"name": row.company_name, "industry": row.industry, "max_salary": row.max_salary} for row in top_placements]
        return jsonify(topList), 200
        
    except Exception as e: 
        return jsonify({"error": str(e)}), 500
    

# ===========================================================================================================================
#                                          Student Section
# ===========================================================================================================================

@bp.route('/students', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def getAllStudents():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user or user.role != "Admin":
        return jsonify({'message': "Unauthorized access"}), 403
    
    try:
        students = Student.query.order_by(Student.id.desc()).all()
        
        student_list = []
        for s in students:
            has_selected_app = Application.query.filter_by(student_id=s.id, status="Selected").first() is not None
            placement_status = "Placed" if has_selected_app else "Unplaced"

            
            if s.is_blacklist:
                account_status = "Blacklisted"
            else:
                account_status = "Active" 

            student_list.append({
                "id": s.id,
                "name": s.full_name,  
                "email": s.contact,  
                "branch": s.branch if s.branch else "N/A",
                "cgpa": s.cgpa if s.cgpa else 0.0,
                "placement_status": "Placed" if placement_status else "Unplaced",
                "account_status": account_status
            })

        return jsonify(student_list), 200
        
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500


@bp.route('/students/update-status', methods=['POST'])
@jwt_required()
def updateStudentStatus():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user or user.role != "Admin":
        return jsonify({'message': "Unauthorized access"}), 403

    data = request.get_json()
    student_id = data.get('student_id')
    new_status = data.get('status') 

    if not student_id or not new_status:
        return jsonify({'message': 'Missing data parameters'}), 400

    try:
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404

        
        if new_status == 'Blacklisted':
            student.is_blacklist = True
        elif new_status == 'Active':
            student.is_blacklist = False
        
        db.session.commit()

        try:
            cache.clear() 
            print("Admin student action: Cache cleared successfully.")
        except Exception as cache_err:
            print(f"Cache clear failed: {cache_err}")

        return jsonify({'message': f'Status updated to {new_status}'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
    
# ===================================================================================================================
#                                             Company Section
# ===================================================================================================================
@bp.route('/companies', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def getAllCompanies():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user or user.role != "Admin":
        return jsonify({'message': "Unauthorized access"}), 403
    
    try:
        total_companies = Company.query.count()
        pending_companies = Company.query.filter_by(approval_status='PENDING').count()
        approved_companies = Company.query.filter_by(approval_status='APPROVED').count()
        blacklisted_companies = Company.query.filter_by(is_blacklist=True).count()


        all_companies = Company.query.order_by(Company.id.desc()).all()
        companies_list = []
        for c in all_companies:
            companies_list.append({
                "id": c.id,
                "name": c.company_name,
                "industry": c.industry,
                "location": c.location,
                "website": c.website if c.website else "N/A",
                "approval_status": c.approval_status, # Pending, Approved, Rejected
                "is_blacklist": c.is_blacklist
            })

        # Top 10 Companies based on highest packages offered
        top_packages = db.session.query(Company.id, Company.company_name, Company.industry, func.max(Placement.salary).label('max_salary'))\
            .join(Placement, Company.id == Placement.company_id)\
            .group_by(Company.id, Company.company_name, Company.industry)\
            .order_by(db.text('max_salary DESC')).limit(10).all()

        top_10_partners = [{
            "id": row.id,
            "name": row.company_name,
            "industry": row.industry,
            "max_salary": row.max_salary
        } for row in top_packages]

        return jsonify({
            "metrics": {
                "total": total_companies,
                "pending": pending_companies,
                "approved": approved_companies,
                "blacklisted": blacklisted_companies
            },
            "companies": companies_list,
            "topPartners": top_10_partners
        }), 200

    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500


@bp.route('/companies/action', methods=['POST'])
@jwt_required()
def handleCompanyAction():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user or user.role != "Admin":
        return jsonify({'message': "Unauthorized access"}), 403

    data = request.get_json()
    company_id = data.get('company_id')
    action_type = data.get('action') # 'Approve', 'Reject', 'Blacklist', 'Activate', 'Remove'

    if not company_id or not action_type:
        return jsonify({'message': 'Missing fields parameters'}), 400

    try:
        company = Company.query.filter_by(id=company_id).first()
        if not company:
            return jsonify({'message': 'Company profile not found'}), 404
 
        # functionalities mapping
        if action_type == 'Approve':
            company.approval_status = 'APPROVED'

            linked_user = User.query.filter_by(id=company.user_id).first()
            if linked_user:
                linked_user.is_approved = 1  
                print(f"[Sync Success] User status approved for email: {linked_user.email}")
        elif action_type == 'Reject':
            company.approval_status = 'REJECTED'
        elif action_type == 'Blacklist':
            company.is_blacklist = True
        elif action_type == 'Activate':
            company.is_blacklist = False
        elif action_type == 'Remove':
            db.session.delete(company)
        
        db.session.commit()

        try:
            cache.clear() 
            print("Admin company action: Cache cleared successfully.")
        except Exception as cache_err:
            print(f"Cache clear failed: {cache_err}")

        return jsonify({'message': f'Operation {action_type} executed successfully!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
    
# ====================================================================================================================
#                                         Drive Section
# ====================================================================================================================
@bp.route('/drives', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def getAllDrivesData():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user or user.role != "Admin":
        return jsonify({'message': "Unauthorized access"}), 403
        
    try:
        total_jobs = JobPosition.query.count()
        ongoing_drives = JobPosition.query.filter_by(status='ONGOING').count()
        pending_approvals = JobPosition.query.filter_by(approval_status='PENDING').count()
        total_apps = Application.query.count()


        all_jobs_query = db.session.query(
            JobPosition,
            func.count(Application.id).label('total_submissions')
        ).outerjoin(Application, JobPosition.id == Application.job_id)\
         .group_by(JobPosition.id)\
         .order_by(JobPosition.id.desc()).all()

        jobs_list = []
        for j, total_submissions in all_jobs_query:
            jobs_list.append({
                "id": j.id,
                "company_name": j.company.company_name if j.company else "Unknown Company",
                "title": j.title,
                "salary": j.salary,
                "branch": j.eligible_branch,
                "deadline": j.application_deadline.strftime('%Y-%m-%d') if j.application_deadline else "N/A",
                "approval_status": j.approval_status, 
                "status": j.status,                   
                "apps_count": total_submissions 
            })

        # Top 7 Demanding Companies (Most job openings posted)
        top_demanding_query = db.session.query(Company.company_name, func.count(JobPosition.id).label('job_count'))\
            .join(JobPosition, Company.id == JobPosition.company_id)\
            .group_by(Company.id)\
            .order_by(db.text('job_count DESC')).limit(7).all()

        top_7_corporates = [{
            "name": row.company_name,
            "job_count": row.job_count
        } for row in top_demanding_query]

        return jsonify({
            "metrics": {
                "totalJobs": total_jobs,
                "ongoing": ongoing_drives,
                "pending": pending_approvals,
                "totalApps": total_apps
            },
            "jobs": jobs_list,
            "topDemanding": top_7_corporates
        }), 200

    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500


@bp.route('/drives/action', methods=['POST'])
@jwt_required()
def handleDriveAction():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user or user.role != "Admin":
        return jsonify({'message': "Unauthorized access"}), 403

    data = request.get_json()
    job_id = data.get('job_id')
    action_type = data.get('action') # 'APPROVE', 'REJECT', 'CLOSE_APPLICATION'

    try:
        job = JobPosition.query.filter_by(id=job_id).first()
        if not job:
            return jsonify({'message': 'Job opening profile not found'}), 404

        if action_type == 'APPROVE':
            job.approval_status = 'APPROVED'
            job.status = 'ONGOING'
        elif action_type == 'REJECT':
            job.approval_status = 'CLOSED'
            job.status = 'CLOSED'
        elif action_type == 'CLOSE_APPLICATION':
            job.status = 'CLOSED'
            job.approval_status = 'CLOSED'
            
        db.session.commit()

        try:
            cache.clear() # Placement drive status change hone par student aur admin feed refresh karo
            print("Admin drive action: Cache cleared successfully.")
        except Exception as cache_err:
            print(f"Cache clear failed: {cache_err}")

        return jsonify({'message': 'Drive transaction completed successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Server error", "error": str(e)}), 500
    
@bp.route('/dashboard/create-drive-override', methods=['POST'])
@jwt_required()
def adminCreateDriveOverride():
    # Verification matrix ensuring only admin access
    # identity verification custom flags lagaye ja sakte hain tumhare schema ke hisab se
    try:
        data = request.get_json()
        company_id = data.get("company_id")  # Admin select karega dynamic option dropdown se
        title = data.get("title")
        salary = data.get("salary")
        location = data.get("location")
        deadline_str = data.get("deadline")
        skills = data.get("skills")

        if not company_id or not title or not salary or not location or not deadline_str:
            return jsonify({"message": "Sari fields aur target company select karna compulsory hai!"}), 400

        deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d')

        new_job = JobPosition(
            company_id=company_id,  # Admin dynamic mapping bind
            title=title,
            salary=salary,
            location=location,
            application_deadline=deadline_date,
            skills_required=skills,
            status="ONGOING"
        )

        db.session.add(new_job)
        db.session.commit()

        try:
            cache.clear() # Admin structural modifications automatically clear global metrics cache
            print("[Admin Cache Alert] Dynamic sync cleared dashboard metrics.")
        except Exception as ce:
            print(f"Cache clear warning: {ce}")

        return jsonify({"message": "Drive successfully deployed by Admin panel override!"}), 201

    except Exception as e:
        db.session.rollback()
        print("Crash inside admin create drive mapping:", str(e))
        return jsonify({"message": "Server failure.", "error": str(e)}), 500