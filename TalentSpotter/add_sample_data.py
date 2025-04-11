import json
import os
from datetime import datetime
from app import app, db
from models import JobDescription, Candidate

def add_sample_data():
    """Add sample data to the database for testing"""
    print("Adding sample data to the database...")
    
    # First check if we already have data
    job_count = JobDescription.query.count()
    candidate_count = Candidate.query.count()
    
    if job_count > 0 or candidate_count > 0:
        print(f"Database already has {job_count} jobs and {candidate_count} candidates.")
        if input("Do you want to proceed anyway? (y/n): ").lower() != 'y':
            print("Exiting without making changes.")
            return
    
    # Sample job
    if job_count == 0:
        job = JobDescription(
            job_title="Senior Software Engineer",
            department="Engineering",
            required_experience=5,
            required_education="Bachelor's degree in Computer Science or related field",
            required_skills=json.dumps({
                "technical_skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
                "soft_skills": ["Communication", "Leadership", "Problem Solving"]
            }),
            job_responsibilities=json.dumps([
                "Lead development of new features for our web application",
                "Mentor junior developers and conduct code reviews",
                "Participate in architecture decisions and technical planning",
                "Work with product managers to define requirements and scope",
                "Continuously improve our development processes and tooling"
            ]),
            status="active"
        )
        
        db.session.add(job)
        db.session.commit()
        print(f"Added job: {job.job_title}")
    
    # Sample candidate
    if candidate_count == 0:
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
        
        db.session.add(candidate)
        db.session.commit()
        print(f"Added candidate: {candidate.name}")
    
    print("Sample data added successfully!")

if __name__ == "__main__":
    with app.app_context():
        add_sample_data()
