from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from datetime import datetime, timedelta
from models import db,User, Student, Company
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required, get_jwt_identity, get_jwt



bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login() :
    data = request.json 

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email = email).first()

    if not user:
        return jsonify({'message' : "User Not Found"}), 404

    elif not user.check_password(password):
        return jsonify({'message': 'Password is wrong'}), 401 
    
    if user.role == 'Student' :
        student = Student.query.filter_by(user_id = user.id).first()
        if student and student.is_blacklist :
            return jsonify({'message': 'Your account has been blacklisted. Contact Support Team.'}), 403
        
    if user.role == "Company":
        company_profile = Company.query.filter_by(user_id=user.id).first()
        if not company_profile or company_profile.approval_status != 'APPROVED':
            return jsonify({ "message": "Your company is not approved yet." }), 403
        elif company_profile.is_blacklist:
            return jsonify({ "message": "Your company has been blacklisted." }), 403
        
    if user and user.check_password(password):
        access_token = create_access_token(
                                            identity=str(user.id),
                                            additional_claims={
                                                "role": user.role
                                            })
        
        refreshToken = create_refresh_token(identity=str(user.id),
                                            additional_claims={
                                                "role": user.role
                                            })

        response = jsonify({
            "message": "Login Sucessfully!",
            "accessToken": access_token,
            # "refreshToken" : refreshToken,
            "role": user.role,
            "username": user.username
        }) 

        response.set_cookie(
            "refreshToken", refreshToken, httponly=True , secure=False, samesite='Lax', max_age=7*24*60*60
        )                                           
                                                 # in production , secure=True, Must for Render (HTTPS)
                                                 # Kyunki domains alag hain (Netlify aur Render) so , semantic = None
        return response, 200

@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh() :
    user_id = get_jwt_identity()
    claims = get_jwt()

    role = claims.get("role")

    accessToken = create_access_token(
                                    identity=user_id,
                                    additional_claims={
                                        "role": role
                                    }
    )

    return jsonify({"accessToken" : accessToken}), 200


@bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role') # 'Student' ya 'Company'

    if not all([username, email, password, role]):
        return jsonify({"message": "All fields parameters are mandatory."}), 400

    try:
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({"message": "Username or Email already registered."}), 409


        user_approval_flag = True if role == 'Student' else False

        new_user = User(
            username=username,
            email=email,
            role=role,
            is_approved=user_approval_flag 
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.flush() # user_id instantiate karne ke liye flush chalaya

        # 2. Secondary Table Multi-Role Linking
        if role == 'Student':
            new_student = Student(
                user_id=new_user.id,
                full_name=data.get('full_name', username),
                contact=data.get('contact', ''),
                branch=data.get('branch', 'N/A'),
                cgpa=data.get('cgpa', 0.0),
                is_blacklist=False # Default safe status
            )
            db.session.add(new_student)
            
        elif role == 'Company':
            new_company = Company(
                user_id=new_user.id,
                company_name=data.get('company_name', username),
                industry=data.get('industry', 'Tech'),
                location=data.get('location', 'Delhi'),
                website=data.get('website', f"https://{username.lower()}.com"),
                hr_name=data.get('hr_name', 'HR Desk Lead'),
                hr_email=email,
                approval_status='PENDING', 
                is_blacklist=False
            )
            db.session.add(new_company)

        db.session.commit()
        return jsonify({
            "message": "Registration matrix completed successfully.",
            "role": role
        }), 201

    except Exception as e:
        db.session.rollback()
        print("Registration Crash Alert:", str(e))
        return jsonify({"message": "Server error processing registration", "error": str(e)}), 500
    
