# Placement Portal Cell

A full-stack campus placement management system built with Flask and Vue.js. The project supports student recruitment workflows, company hiring operations, and administrative moderation for a placement office.

## Project Overview

This application is designed to manage the end-to-end placement workflow for a college or training institute. It connects three primary user roles:

- Students who register, build a profile, upload a resume, browse job openings, and apply for placement drives.
- Companies that register, create placement drives, review applicants, shortlist or reject candidates, and export applicant data.
- Admins who approve or reject companies, manage blacklisting, and monitor overall placement activity.

The backend is implemented in Flask with SQLAlchemy, while the frontend is a Vue 2 single-page application using Vue Router. The system also includes Redis-backed caching and a Celery task queue for scheduled and asynchronous jobs.

## Main Features Implemented

### Student Features
- Student registration and login
- Profile management with contact details, branch, CGPA, skills, experience, and PDF resume upload
- Dashboard metrics for applied jobs, shortlisted applications, and offers
- Job exploration feed filtered by ongoing approved drives
- Application submission with eligibility checks based on CGPA and resume presence
- Applied history and status tracking
- Resume preview URL served by the backend

### Company Features
- Company registration with pending approval flow
- Company dashboard with overall metrics and recent drives
- Creation of placement drives with title, salary, location, deadline, and skills
- Drive status management: ongoing or closed
- Applicant review and workflow updates (Pending, Shortlist, Selected, Reject)
- Applicant profile view and interview date tracking
- CSV export for applicants via Celery task
- Downloadable export files stored in the backend static export folder

### Admin Features
- Admin dashboard overview with student count, company count, placement rate, pending approvals, and growth metrics
- Company approval / rejection / blacklist / reactivation actions
- Student blacklist / reactivation actions
- Drive analytics and demand summaries
- Company and drive monitoring for the placement office

### Platform Features
- JWT-based authentication with refresh-token support
- Redis cache for dashboard and job list performance
- Celery periodic jobs for interview reminders and monthly reporting
- SQLite database with seeded mock data for demo scenarios

## User Roles and Functionality

### 1. Student
Students can:
- register with a username, email, password, and profile details
- upload a PDF resume
- view ongoing approved job drives
- apply to eligible jobs
- track application statuses from pending to shortlist or selected
- access personal dashboard metrics and applied history

### 2. Company
Companies can:
- register an HR/company profile
- wait for admin approval before login is allowed
- create and manage placement drives
- review applicants for each job
- update applicant workflow status
- trigger CSV export of candidate data

### 3. Admin
Admins can:
- review the placement dashboard and analytics
- approve or reject company profiles
- blacklist or reactivate company/student accounts
- monitor all active drives and student/company counts
- generate or oversee placement records and reporting data

## Tech Stack

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Flask-Caching
- Flask-Mail
- Celery
- Redis
- SQLite

### Frontend
- Vue 2
- Vue Router
- Vuex
- Axios
- JavaScript
- CSS custom styling

### Tooling
- Python virtual environment (`venv`)
- npm / Vue CLI
- Redis for cache and Celery broker/backend

## Backend and Frontend Architecture

### Backend Architecture
The backend is organized as a Flask application with route blueprints:

- `backend/run.py`: Flask app initialization, config, database setup, cache initialization, Celery config, and blueprint registration
- `backend/models.py`: SQLAlchemy models for users, students, companies, jobs, applications, and placements
- `backend/routes/auth.py`: login, registration, and JWT refresh endpoints
- `backend/routes/student.py`: student dashboards, job exploration, profile update, and application logic
- `backend/routes/company.py`: company dashboard, drive management, applicant workflow, and export routes
- `backend/routes/admin.py`: admin analytics, moderation, and approval workflows
- `backend/task.py`: Celery tasks for CSV export, interview reminders, and monthly analytics reports
- `backend/extension.py`: shared Flask extensions
- `backend/data.py`: seeded demo data used during initial setup

### Frontend Architecture
The frontend is a Vue SPA organized under `frontend/src`:

- `frontend/src/router/index.js`: route definitions for landing, login, registration, student, company, and admin dashboards
- `frontend/src/views`: page-level views
- `frontend/src/components`: role-specific dashboard components
- `frontend/src/main.js`: global Axios configuration and token interceptor setup

The frontend calls the backend through `http://localhost:5000` and stores the JWT access token in `localStorage`.

## Authentication and Authorization Approach

Authentication is implemented with Flask-JWT-Extended.

- User login validates email and password
- JWT access tokens are returned to the client
- Refresh tokens are set as HTTP-only cookies
- Frontend attaches the access token in the `Authorization: Bearer <token>` header
- Protected routes use `@jwt_required()`
- Role-specific logic is enforced in endpoints for students, companies, and admins

The backend also performs account-level checks:
- Students cannot log in if blacklisted
- Companies cannot log in unless their profile is approved and not blacklisted
- Admin-only routes verify the user role before allowing access

## Database and ORM Usage

The project uses Flask-SQLAlchemy with SQLite for the local database.

Database file:
- `backend/instance/placement.db`

Core models defined in `backend/models.py`:
- `User`: account data, password hash, role, approval status
- `Student`: student profile, branch, CGPA, resume path, blacklist flag
- `Company`: company profile, approval status, blacklist flag
- `JobPosition`: job drive details, eligibility criteria, deadlines, status
- `Application`: application records and recruiter decisions
- `Placement`: accepted placement records / placed candidates

The app creates tables automatically at startup using `db.create_all()`.

## Background Tasks and Scheduled Jobs

The project includes Celery and Redis integration for asynchronous work.

### Implemented tasks
- `export_applicants_csv_task`
  - Exports applicant records to a CSV file
  - Triggered from the company applicant workflow
- `send_interview_reminders_task`
  - Looks for applications with interviews scheduled for the next day
  - Sends reminder emails to students
- `generate_monthly_placement_reports`
  - Builds company-level HTML performance reports
  - Saves them under `backend/static/exports`
  - Sends email notifications to the company HR email when available

### Current scheduling configuration
In `backend/run.py`, Celery Beat is configured with:
- interview reminders scheduled daily at 09:00
- monthly report generation configured to run on a short periodic interval during development

This is a working local development pattern, but it is not a production-grade scheduling configuration by itself.

## Reporting Functionality

Implemented reporting includes:
- Applicant CSV export for a specific company
- Company-specific HTML monthly placement summary generated as a static report
- Dashboard metrics and analytics in the admin and company panels

Report outputs are stored in:
- `backend/static/exports/`

Examples from the repository include:
- `backend/static/exports/company_1_monthly_report.html`
- `backend/static/exports/company_18_applicants.csv`
- `backend/static/exports/company_51_applicants.csv`

## Project Folder Structure

```text
Placement Portal Cell/
├── backend/
│   ├── instance/
│   │   └── placement.db
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── company.py
│   │   └── student.py
│   ├── static/
│   │   ├── exports/
│   │   └── uploads/
│   │       └── resumes/
│   ├── data.py
│   ├── extension.py
│   ├── models.py
│   ├── run.py
│   ├── secret.py
│   └── task.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/
│   │   ├── store/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vue.config.js
│   └── README.md
├── .gitignore
├── api.yaml
├── LICENSE
├── package.json
├── README.md
├── requirements.txt
└── ...
```

## Installation and Setup

### Prerequisites
- Python environment with `venv` or similar
- Node.js and npm
- Redis installed and running locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd "Placement Portal Cell"
```

### 2. Create and activate a Python virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

### 5. Start Redis
The project depends on Redis for Flask-Caching and Celery messaging.

```bash
redis-server
```

## Environment Variables

The project currently contains hardcoded configuration values in the codebase, including secret keys and email credentials. For a production-safe setup, move them into environment variables.

Use placeholders like these:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRES_DAYS=7
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@example.com
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///instance/placement.db
FRONTEND_URL=http://localhost:8080
BACKEND_URL=http://localhost:5000
```

> Do not commit actual credentials or secrets in the repository.

## How to Run the Backend

From the project root, activate the environment and then start the Flask app from the backend folder:

```bash
cd backend
python run.py
```

The backend runs on:
- `http://localhost:5000`

### Celery worker and scheduler
If you want to test the async job features:

```bash
cd backend
celery -A run.celery worker --loglevel=info -P solo
```

```bash
cd backend
celery -A run.celery beat --loglevel=info
```

## How to Run the Frontend

From the frontend folder:

```bash
cd frontend
npm run serve
```

The Vue app runs on:
- `http://localhost:8080`

## Key Application Workflows

### Student workflow
1. Register as a student
2. Log in
3. Complete or update profile and resume
4. Browse active approved drives
5. Apply to jobs that match eligibility criteria
6. View application status in the applied history dashboard

### Company workflow
1. Register as a company
2. Wait for admin approval
3. Log in after approval
4. Create a placement drive
5. Review applicants and update their status
6. Export candidate data to CSV or monitor monthly report output

### Admin workflow
1. Log in as admin
2. Review student and company counts
3. Approve, reject, blacklist, or activate company accounts
4. Manage blacklisted students
5. Review drive statuses and platform-level placement analytics

## Future Improvements

These are not currently implemented in the codebase, but would be valuable enhancements:

- Move all secrets and environment-specific config into `.env` files or deployment configuration
- Add proper production-grade email templates and notification system
- Add role-based page guards and route protection on the frontend
- Introduce real database migrations instead of `db.create_all()`
- Replace SQLite with PostgreSQL or MySQL for production deployment
- Improve resume parsing and automated candidate matching
- Add pagination, filtering, and search improvements for large datasets
- Improve test coverage for authentication, application logic, and admin actions
- Add deployment-ready Docker and CI/CD configuration

## Notes

This project is a functional placement management prototype with seeded demo data and local development configuration. It is suitable for academic, portfolio, and demonstration use, and reflects the actual implementation present in the repository.

## License

This project is licensed under the MIT license. See the `LICENSE` file for details.
