import json
import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Candidate model (minimally, just for this script)
class Candidate(db.Model):
    """Model for candidates"""
    __tablename__ = 'candidates'
    
    candidate_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    education = db.Column(db.Text)  # JSON as text
    experience = db.Column(db.Text)  # JSON as text
    skills = db.Column(db.Text)  # JSON as text
    certifications = db.Column(db.Text)  # JSON as text
    cv_text = db.Column(db.Text)  # Store the extracted text from CV
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def add_sample_candidate():
    """Add a sample candidate to the database"""
    try:
        # Sample candidate data
        candidate = Candidate(
            name="John Smith",
            email="john.smith@example.com",
            phone="555-123-4567",
            education=json.dumps([
                {
                    "institution": "Stanford University",
                    "degree": "Master of Science",
                    "field_of_study": "Computer Science",
                    "start_year": 2015,
                    "end_year": 2017
                },
                {
                    "institution": "University of California, Berkeley",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Engineering",
                    "start_year": 2011,
                    "end_year": 2015
                }
            ]),
            experience=json.dumps([
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Innovations Inc.",
                    "start_date": "2020-01",
                    "end_date": None,
                    "description": "Leading a team of 5 developers working on a cloud-based analytics platform. Implemented microservices architecture and CI/CD pipeline."
                },
                {
                    "title": "Software Engineer",
                    "company": "DataSoft Solutions",
                    "start_date": "2017-06",
                    "end_date": "2019-12",
                    "description": "Developed RESTful APIs and frontend components for a customer management system. Improved performance by 40%."
                },
                {
                    "title": "Software Developer Intern",
                    "company": "WebTech Startups",
                    "start_date": "2016-05",
                    "end_date": "2016-08",
                    "description": "Assisted in developing a mobile application using React Native. Implemented user authentication and data synchronization."
                }
            ]),
            skills=json.dumps({
                "Python": 90,
                "JavaScript": 85,
                "React": 80,
                "Node.js": 75,
                "AWS": 70,
                "Docker": 80,
                "Kubernetes": 65,
                "SQL": 85,
                "MongoDB": 75,
                "Leadership": 90,
                "Communication": 95,
                "Problem Solving": 90
            }),
            certifications=json.dumps([
                {
                    "name": "AWS Certified Solutions Architect",
                    "issuer": "Amazon Web Services",
                    "year": 2021
                },
                {
                    "name": "Certified Scrum Master",
                    "issuer": "Scrum Alliance",
                    "year": 2019
                }
            ]),
            cv_text="""
John Smith
Senior Software Engineer

Contact:
Email: john.smith@example.com
Phone: 555-123-4567
LinkedIn: linkedin.com/in/johnsmith

Summary:
Experienced Senior Software Engineer with 5+ years of professional experience in full-stack development. Skilled in Python, JavaScript, React, Node.js, and AWS. Strong track record of leading development teams and delivering high-quality software solutions.

Education:
- Master of Science in Computer Science, Stanford University, 2015-2017
- Bachelor of Science in Computer Engineering, University of California, Berkeley, 2011-2015

Experience:
Senior Software Engineer, Tech Innovations Inc., Jan 2020 - Present
- Lead a team of 5 developers working on a cloud-based analytics platform
- Implemented microservices architecture and CI/CD pipeline
- Reduced system downtime by 75% through improved monitoring and automated recovery
- Mentor junior developers and conduct regular code reviews
- Collaborate with product managers to define requirements and prioritize features

Software Engineer, DataSoft Solutions, Jun 2017 - Dec 2019
- Developed RESTful APIs and frontend components for a customer management system
- Improved application performance by 40% through code optimization and database indexing
- Implemented automated testing, increasing code coverage from 45% to 90%
- Participated in agile development process, contributing to planning and retrospectives

Software Developer Intern, WebTech Startups, May 2016 - Aug 2016
- Assisted in developing a mobile application using React Native
- Implemented user authentication and data synchronization features
- Created automated UI tests using Detox

Skills:
- Programming Languages: Python, JavaScript, TypeScript, Java, C++
- Frontend: React, Angular, HTML5, CSS3, SASS
- Backend: Node.js, Express, Django, Flask
- Databases: PostgreSQL, MongoDB, Redis
- DevOps: AWS, Docker, Kubernetes, CI/CD, Jenkins
- Tools: Git, JIRA, Confluence, VS Code, Postman
- Soft Skills: Leadership, Communication, Problem Solving, Teamwork

Certifications:
- AWS Certified Solutions Architect, 2021
- Certified Scrum Master, 2019

Projects:
- Analytics Dashboard: Led development of a real-time analytics dashboard using React, D3.js, and WebSockets
- Inventory Management System: Designed and implemented a serverless inventory tracking system using AWS Lambda and DynamoDB
- Open Source Contributions: Active contributor to several open source projects in the Python ecosystem
            """
        )
        
        # Add the candidate to the database
        with app.app_context():
            # First check if we have any candidates
            existing_count = db.session.query(Candidate).count()
            logger.info(f"Found {existing_count} existing candidates in the database")
            
            if existing_count == 0:
                db.session.add(candidate)
                db.session.commit()
                logger.info(f"Added sample candidate: {candidate.name}")
            else:
                logger.info("Database already has candidates, skipping sample data creation")
        
        return True
    except Exception as e:
        logger.error(f"Error adding sample candidate: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_sample_candidate()
    if success:
        print("✅ Sample candidate added successfully!")
    else:
        print("❌ Failed to add sample candidate. Check the logs for details.")
        sys.exit(1)
