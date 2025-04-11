import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
import logging
from typing import Dict, List, Optional
import jinja2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.email_username = os.getenv('EMAIL_USERNAME')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.template_loader = jinja2.FileSystemLoader('TalentSpotter/templates/emails')
        self.template_env = jinja2.Environment(loader=self.template_loader)

    def send_interview_invitation(self, candidate: Dict, job: Dict, template_name: str = 'interview_invitation.html') -> bool:
        """Send interview invitation email to candidate."""
        try:
            # Load email template
            template = self.template_env.get_template(template_name)
            
            # Prepare email content
            email_content = template.render(
                candidate=candidate,
                job=job,
                company_name=os.getenv('COMPANY_NAME', 'Your Company'),
                company_logo=os.getenv('COMPANY_LOGO_URL', ''),
                interview_date=job.get('interview_date', 'To be scheduled'),
                interview_location=job.get('interview_location', 'Virtual')
            )

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Interview Invitation - {job['title']}"
            msg['From'] = self.email_username
            msg['To'] = candidate['email']

            # Attach HTML and plain text versions
            msg.attach(MIMEText(email_content, 'html'))
            msg.attach(MIMEText(self._generate_plain_text(email_content), 'plain'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_username, self.email_password)
                server.send_message(msg)

            # Log success
            logger.info(f"Interview invitation sent to {candidate['email']}")
            return True

        except Exception as e:
            logger.error(f"Error sending interview invitation: {str(e)}")
            return False

    def _generate_plain_text(self, html_content: str) -> str:
        """Generate plain text version of HTML email."""
        # Simple HTML to plain text conversion
        import re
        text = re.sub('<[^<]+?>', '', html_content)
        text = re.sub('\s+', ' ', text)
        return text.strip()

    def track_email_status(self, email_id: str, status: str, details: Optional[Dict] = None) -> None:
        """Track email status and update database."""
        try:
            # Implement email tracking logic
            tracking_data = {
                'email_id': email_id,
                'status': status,
                'timestamp': datetime.utcnow(),
                'details': details or {}
            }
            # Add to database or tracking system
            logger.info(f"Email {email_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Error tracking email status: {str(e)}")

    def send_bulk_invitations(self, candidates: List[Dict], job: Dict) -> Dict[str, bool]:
        """Send interview invitations to multiple candidates."""
        results = {}
        for candidate in candidates:
            email_id = f"{candidate['email']}_{datetime.utcnow().timestamp()}"
            success = self.send_interview_invitation(candidate, job)
            results[email_id] = success
            self.track_email_status(email_id, 'sent' if success else 'failed')
        return results

    def send_interview_scheduled_email(self, interview, job, candidate):
        """Send email notification for scheduled interview"""
        subject = f"Interview Scheduled: {job.title} Position"
        
        body = f"""
        Dear {candidate.name},
        
        Your interview for the {job.title} position has been scheduled.
        
        Details:
        - Date: {interview.scheduled_date.strftime('%B %d, %Y')}
        - Time: {interview.scheduled_date.strftime('%I:%M %p')}
        - Format: {interview.format}
        
        Please let us know if you need to reschedule or have any questions.
        
        Best regards,
        TalentSpotter Team
        """
        
        return self.send_email(candidate.email, subject, body)

    def send_interview_feedback_email(self, interview, job, candidate, feedback):
        """Send email with interview feedback"""
        subject = f"Interview Feedback: {job.title} Position"
        
        body = f"""
        Dear {candidate.name},
        
        Thank you for interviewing for the {job.title} position.
        
        Feedback:
        {feedback}
        
        Best regards,
        TalentSpotter Team
        """
        
        return self.send_email(candidate.email, subject, body)

    def send_email(self, email: str, subject: str, body: str) -> bool:
        """Send a simple email."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_username
            msg['To'] = email

            # Attach plain text version
            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_username, self.email_password)
                server.send_message(msg)

            # Log success
            logger.info(f"Email sent to {email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False 