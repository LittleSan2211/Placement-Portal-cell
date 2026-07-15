STUDENT_NAMES = [
    "Hori",
    "Miyuki",
    "Yumiko",
    "Shizuka",
    "Sakura",
    "Aika",
    "Yuki",
    "Hinata",
    "Akari",
    "Rika",
    "Nanami",
    "Misaki",
    "Hina",
    "Ayame",
    "Kaori",
    "Sora",
    "Chika",
    "Natsumi",
    "Airi",
    "Koharu",
    "Emilia",
    "Rem",
    "Asuna",
    "Mikasa",
    "Violet",
    "Elaina",
    "Roxy",
    "Marin",
    "Kaguya",
    "Chizuru",
    "Xun'er",
    "Ziyan",
    "Qingyue",
    "Yueru",
    "Lingxi",
    "Yun'er",
    "Qingxue",
    "Meilin",
    "Lianhua",
    "Ruolan",
    "Medusa",
    "Seraphina",
    "Aurelia",
    "Celestia",
    "Lunaria",
    "Evangeline",
    "Rosalina",
    "Sylphie",
    "Aria",
    "Qilin",
]

COMPANY_NAMES = [
    "Google",
    "Microsoft",
    "Piyu",
    "Amazon",
    "Meta",
    "Netflix",
    "Apple",
    "Adobe",
    "Oracle",
    "Salesforce",
    "Infosys",
    "TCS",
    "Wipro",
    "HCLTech",
    "Accenture",
    "Deloitte",
    "Capgemini",
    "Cognizant",
    "IBM",
    "Intel",
    "Nvidia",
    "Samsung",
    "Sony",
    "Flipkart",
    "Paytm",
    "Zomato",
    "Swiggy",
    "PhonePe",
    "Razorpay",
    "Freshworks",
    "Zoho",
    "Atlassian",
    "Uber",
    "Airbnb",
    "Spotify",
    "Shopify",
    "Stripe",
    "Dropbox",
    "GitHub",
    "GitLab",
    "Canva",
    "Notion",
    "Figma",
    "Slack",
    "Twilio",
    "MongoDB",
    "Databricks",
    "Snowflake",
    "ServiceNow",
    "Cisco",
]

JOB_TITLES = [
    "Software Engineer",
    "ML Engineer",
    "Data Scientist",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Data Analyst",
    "Business Analyst",
    "QA Engineer",
    "Automation Tester",
    "UI UX Designer",
    "Product Manager",
    "Cyber Security Analyst",
    "Database Administrator",
    "Mobile App Developer",
    "AI Engineer",
    "System Engineer",
    "Network Engineer",
    "Site Reliability Engineer",
    "Python Developer",
    "Java Developer",
    "React Developer",
    "Vue Developer",
    "Angular Developer",
    "Node.js Developer",
    "Flask Developer",
    "Django Developer",
    "Spring Boot Developer",
    "Android Developer",
    "iOS Developer",
    "Blockchain Developer",
    "Game Developer",
    "AR VR Developer",
    "Embedded Engineer",
    "Big Data Engineer",
    "Data Engineer",
    "Research Engineer",
    "Technical Consultant",
    "Solutions Architect",
    "Support Engineer",
    "Security Engineer",
    "NLP Engineer",
    "Computer Vision Engineer",
    "MLOps Engineer",
    "ETL Developer",
    "Power BI Developer",
    "CRM Developer",
    "Technical Writer",
]

BRANCHES = ["CSE", "IT", "DS", "AIML", "ECE"]
SKILLS = [
    "Java, Python, SQL, DL, ML",
    "Python, Flask, Vue.js, SQL",
    "Java, Spring Boot, MySQL",
    "React, Node.js, MongoDB",
    "Python, Pandas, Power BI",
]
LOCATIONS = [
    "Bangalore",
    "Hyderabad",
    "Pune",
    "Delhi",
    "Mumbai",
    "Chennai",
    "Noida",
    "Gurgaon",
    "Kolkata",
    "Indore",
]
APPLICATION_STATUS = [
    "Reject",
    "Reject",
    "Shortlist",
    "Shortlist",
    "Shortlist",
    "Shortlist",
    "Selected",
    "Selected",
]
JOB_TYPES = ["Full Time", "Internship"]
COMMON_RESUME_PATH = "uploads/resumes/dummy_resume.pdf"


def make_username(name):
    return name.replace("'", "").replace(" ", "")


COMPANIES_DATA = [
    {
        "username": f"{company_name.lower().replace(' ', '_')}_hr",
        "company_name": company_name,
        "about": f"{company_name} is a technology company offering software, data, cloud, and engineering solutions.",
        "industry": "Tech",
        "location": LOCATIONS[index % len(LOCATIONS)],
        "website": f"https://{company_name.lower().replace(' ', '')}.com",
        "hr_name": f"{company_name} HR",
    }
    for index, company_name in enumerate(COMPANY_NAMES)
]

STUDENTS_DATA = [
    {
        "username": make_username(name),
        "full_name": f"{name} Kashyap",
        "contact": str(9000000000 + index),
        "about": f"{name} is a motivated student interested in software development and data technologies.",
        "branch": BRANCHES[index % len(BRANCHES)],
        "year": 2024 + (index % 3),
        "cgpa": round(6.5 + ((index % 8) * 0.4), 1),
        "skills": SKILLS[index % len(SKILLS)],
        "experience": "Built academic and personal projects using modern development tools.",
        "resume_path": COMMON_RESUME_PATH,
    }
    for index, name in enumerate(STUDENT_NAMES)
]

JOBS_DATA = [
    {
        "company_name": company_name,
        "job_type": JOB_TYPES[0] if job_index < 6 else JOB_TYPES[1],
        "title": JOB_TITLES[(company_index + job_index) % len(JOB_TITLES)],
        "description": f"Campus hiring role at {company_name} for skilled and motivated candidates.",
        "benefits": "Health insurance, learning budget, flexible work, and performance bonus.",
        "salary": 600000 + (((company_index + job_index) % 25) * 50000),
        "skills_required": SKILLS[(company_index + job_index) % len(SKILLS)],
        "eligible_branch": ", ".join(BRANCHES[: 2 + (job_index % 4)]),
        "eligible_year": 2024 + (job_index % 3),
        "cgpa": round(6.0 + ((job_index % 6) * 0.5), 1),
        "location": LOCATIONS[(company_index + job_index) % len(LOCATIONS)],
        "approval_status": "APPROVED",
        "status": "ONGOING" if job_index < 6 else "CLOSED",
    }
    for company_index, company_name in enumerate(COMPANY_NAMES)
    for job_index in range(9)
]

APPLICATIONS_DATA = [
    {
        "student_username": student["username"],
        "company_name": JOBS_DATA[(student_index * 8 + application_index) % len(JOBS_DATA)]["company_name"],
        "job_title": JOBS_DATA[(student_index * 8 + application_index) % len(JOBS_DATA)]["title"],
        "status": APPLICATION_STATUS[application_index],
        "feedback": (
            f"{student['full_name']} application marked as "
            f"{APPLICATION_STATUS[application_index]}."
        ),
    }
    for student_index, student in enumerate(STUDENTS_DATA)
    for application_index in range(8)
]

JOB_LOOKUP = {
    (job["company_name"], job["title"]): job
    for job in JOBS_DATA
}

PLACEMENTS_DATA = [
    {
        "student_username": application["student_username"],
        "company_name": application["company_name"],
        "job_title": application["job_title"],
        "salary": JOB_LOOKUP[(application["company_name"], application["job_title"])]["salary"],
        "offer_letter_path": (
            f"offers/{application['student_username']}_"
            f"{application['job_title'].replace(' ', '_')}.pdf"
        ),
    }
    for application in APPLICATIONS_DATA
    if application["status"] == "Selected"
]
