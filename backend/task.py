import os
import csv
from extension import celery
from datetime import datetime, timedelta
from models import db, Application, Student, Company, Placement, User, JobPosition
from flask_mail import Message

@celery.task(name='task.export_applicants_csv_task')
def export_applicants_csv_task(company_id):
    print(f"[Celery] Starting CSV export for Company ID: {company_id}")
    # Local runtime context map to avoid circular load
    from run import app
    with app.app_context(): 
        export_dir = os.path.join(os.getcwd(), 'static', 'exports')
        os.makedirs(export_dir, exist_ok=True)

        file_name = f"company_{company_id}_applicants.csv"
        file_path = os.path.join(export_dir, file_name)

        applications = Application.query.filter(Application.job.has(company_id=company_id)).all()

        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Application ID', 'Student Name', 'Branch', 'Status', 'Feedback'])

            for app_record in applications:
                student = app_record.student
                writer.writerow([
                    app_record.id,
                    student.full_name if student else "Unknown",
                    student.branch if student else "N/A",
                    app_record.status,
                    app_record.feedback
                ])

        print(f"[Celery] CSV Export finished! Saved at: {file_path}")
        return {"status": "SUCCESS", "file_path": file_path, "file_name": file_name}
    
@celery.task(name='task.send_interview_reminders_task')  # bind=True, max_retries=3, default_retry_delay=60
def send_interview_reminders_task():
    from run import app, mail
    with app.app_context():
        tomorrow_start = datetime.combine(datetime.utcnow().date() + timedelta(days=1), datetime.min.time())
        tomorrow_end = datetime.combine(datetime.utcnow().date() + timedelta(days=1), datetime.max.time())
        
        print(f"[Celery Beat] Checking database for interviews between: {tomorrow_start} and {tomorrow_end}")
        
        upcoming_interviews = (
            db.session.query(Application)
            .filter(Application.interview_date >= tomorrow_start, Application.interview_date <= tomorrow_end)
            .all()
        )
        
        for app_record in upcoming_interviews:
            student = app_record.student
            if student:
                student_user = db.session.query(User).filter_by(id=student.user_id).first()
                if student_user:
                    student_email = student_user.email
                    
                    msg = Message(
                        subject="Reminder: Interview Scheduled Tomorrow",
                        recipients=[student_email],
                        body=f"Hi {student.full_name},\n\nThis is a reminder for your upcoming interview tomorrow for Job ID: {app_record.job_id}.\n\nBest of Luck!"
                    )
                    
                    mail.send(msg) 
                    print(f"[MAIL SENT] Successfully sent to {student_email}")
        print(f"[Celery Beat] Interview reminder job completed. Processed {len(upcoming_interviews)} records.")

@celery.task(name='task.generate_monthly_placement_reports')
def generate_monthly_placement_reports():
    print(f"[Celery Beat] Starting Monthly Analytics Report Generation Pipeline: {datetime.utcnow()}")
    from run import app, mail
    with app.app_context():
        try:
            companies = Company.query.all()
            exports_dir = os.path.join(os.getcwd(), 'static', 'exports')
            os.makedirs(exports_dir, exist_ok=True)

            for company in companies:
                # 1. Processing Data Matrix
                jobs = JobPosition.query.filter_by(company_id=company.id).all()
                total_drives = len(jobs)
                
                total_apps = 0
                shortlisted = 0
                selected = 0

                for job in jobs:
                    total_apps += len(job.applications)
                    shortlisted += sum(1 for app in job.applications if app.status == 'Shortlist')
                    selected += sum(1 for app in job.applications if app.status == 'Selected')

                success_rate = round((selected / total_apps * 100), 1) if total_apps > 0 else 0.0

                # 2. Dynamic Premium HTML Templates Generation
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; color: #1e293b; background-color: #f8fafc; }}
                        .report-card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
                        .header {{ border-bottom: 2px solid #4f46e5; padding-bottom: 16px; margin-bottom: 24px; }}
                        .header h2 {{ color: #4f46e5; margin: 0; font-size: 24px; }}
                        .metrics-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 20px; }}
                        .metric-tile {{ background: #f1f5f9; padding: 20px; border-radius: 8px; border-left: 4px solid #4f46e5; }}
                        .m-title {{ font-size: 13px; font-weight: 600; color: #64748b; text-transform: uppercase; }}
                        .m-val {{ font-size: 28px; font-weight: 700; color: #0f172a; margin-top: 6px; }}
                    </style>
                </head>
                <body>
                    <div class="report-card">
                        <div class="header">
                            <h2>Placement Hub — Monthly Recruiter Analytics</h2>
                            <p style="font-weight: 600; margin: 6px 0 0 0;">Corporate Channel: {company.company_name}</p>
                            <p style="font-size: 12px; color: #64748b; margin: 4px 0 0 0;">Timeline Axis: {datetime.utcnow().strftime('%B %Y')}</p>
                        </div>
                        <div class="metrics-grid">
                            <div class="metric-tile"><div class="m-title">Total Job Pools Launched</div><div class="m-val">{total_drives}</div></div>
                            <div class="metric-tile"><div class="m-title">Total Applications Processed</div><div class="m-val">{total_apps}</div></div>
                            <div class="metric-tile"><div class="m-title">Shortlisted Pools</div><div class="m-val">{shortlisted}</div></div>
                            <div class="metric-tile"><div class="m-title">Conversion Rate Metrics</div><div class="m-val">{success_rate}%</div></div>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # 3. Save to Dashboard Static Directory
                report_filename = f"company_{company.id}_monthly_report.html"
                report_path = os.path.join(exports_dir, report_filename)
                
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                print(f"[Dashboard Sync] HTML Report saved for {company.company_name} at {report_path}")

                # 4. Email Broadcast Integration
                # Fallback checking agar hr_email database me available ho, nahi toh support use karein
                target_email = company.hr_email if hasattr(company, 'hr_email') and company.hr_email else None
                
                if target_email:
                    msg = Message(
                        subject=f"Placement Hub: Your Monthly Recruiting Performance Analytics Report",
                        recipients=[target_email],
                        body=f"Dear Placement Partner,\n\nYour recruitment performance analytics report for this month is ready.\n\nYou can access it directly inside your Corporate Portal dashboard, or download your dynamic file using the link below:\nhttp://localhost:5000/company/dashboard/applicants/download-report/{report_filename}\n\nThank you for collaborating with our Institute Placement Cell!"
                    )
                    mail.send(msg)
                    print(f"[Mail Alert Complete] Broadcast sent to corporate HR: {target_email}")

            return "All monthly performance charts compiled and distributed successfully."
        
        except Exception as e:
            print(f"[CRITICAL FAILURE] Pipeline execution failed: {str(e)}")
            return f"Error: {str(e)}"