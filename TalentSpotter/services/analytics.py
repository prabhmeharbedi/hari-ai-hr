import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from sqlalchemy import func
from ..models import db, Analytics, Candidate, Job, Shortlist, EmailTracking

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.enable_analytics = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
        self.retention_days = int(os.getenv('ANALYTICS_RETENTION_DAYS', 90))
        self.track_email_opens = os.getenv('TRACK_EMAIL_OPENS', 'True').lower() == 'true'
        self.track_email_clicks = os.getenv('TRACK_EMAIL_CLICKS', 'True').lower() == 'true'

    def track_metric(self, metric_name: str, metric_value: float, details: Optional[Dict] = None) -> None:
        """Track a metric with optional details."""
        if not self.enable_analytics:
            return

        try:
            analytics = Analytics(
                metric_name=metric_name,
                metric_value=metric_value,
                details=str(details) if details else None
            )
            db.session.add(analytics)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error tracking metric {metric_name}: {str(e)}")
            db.session.rollback()

    def get_match_score_history(self, candidate_id: int) -> List[Dict]:
        """Get match score history for a candidate."""
        try:
            metrics = Analytics.query.filter_by(
                metric_name='match_score',
                details=f"candidate_id:{candidate_id}"
            ).order_by(Analytics.timestamp.desc()).all()
            
            return [{
                'timestamp': m.timestamp.isoformat(),
                'value': m.metric_value,
                'details': eval(m.details) if m.details else {}
            } for m in metrics]
        except Exception as e:
            logger.error(f"Error getting match score history: {str(e)}")
            return []

    def get_shortlist_stats(self) -> Dict:
        """Get statistics about shortlists."""
        try:
            total_shortlists = Shortlist.query.count()
            active_shortlists = Shortlist.query.filter_by(status='active').count()
            avg_candidates_per_shortlist = db.session.query(
                func.avg(func.count(Shortlist.candidates))
            ).group_by(Shortlist.id).scalar() or 0

            return {
                'total_shortlists': total_shortlists,
                'active_shortlists': active_shortlists,
                'avg_candidates_per_shortlist': round(avg_candidates_per_shortlist, 2)
            }
        except Exception as e:
            logger.error(f"Error getting shortlist stats: {str(e)}")
            return {}

    def get_email_metrics(self) -> Dict:
        """Get email tracking metrics."""
        try:
            total_emails = EmailTracking.query.count()
            opened_emails = EmailTracking.query.filter(EmailTracking.opened_at.isnot(None)).count()
            clicked_emails = EmailTracking.query.filter(EmailTracking.clicked_at.isnot(None)).count()

            return {
                'total_emails': total_emails,
                'opened_emails': opened_emails,
                'clicked_emails': clicked_emails,
                'open_rate': round((opened_emails / total_emails * 100) if total_emails > 0 else 0, 2),
                'click_rate': round((clicked_emails / total_emails * 100) if total_emails > 0 else 0, 2)
            }
        except Exception as e:
            logger.error(f"Error getting email metrics: {str(e)}")
            return {}

    def get_candidate_progress(self, candidate_id: int) -> Dict:
        """Get progress metrics for a candidate."""
        try:
            candidate = Candidate.query.get(candidate_id)
            if not candidate:
                return {}

            applications = candidate.applications
            shortlists = [sc.shortlist for sc in candidate.shortlists]
            emails = candidate.email_tracking

            return {
                'total_applications': len(applications),
                'total_shortlists': len(shortlists),
                'active_shortlists': len([s for s in shortlists if s.status == 'active']),
                'total_emails': len(emails),
                'opened_emails': len([e for e in emails if e.opened_at]),
                'clicked_emails': len([e for e in emails if e.clicked_at]),
                'average_match_score': sum(a.match_score for a in applications) / len(applications) if applications else 0
            }
        except Exception as e:
            logger.error(f"Error getting candidate progress: {str(e)}")
            return {}

    def cleanup_old_data(self) -> None:
        """Clean up analytics data older than retention period."""
        if not self.enable_analytics:
            return

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            Analytics.query.filter(Analytics.timestamp < cutoff_date).delete()
            db.session.commit()
            logger.info("Old analytics data cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up old analytics data: {str(e)}")
            db.session.rollback()

    def generate_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate analytics report for a date range."""
        try:
            metrics = Analytics.query.filter(
                Analytics.timestamp.between(start_date, end_date)
            ).all()

            report = {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'metrics': {}
            }

            for metric in metrics:
                if metric.metric_name not in report['metrics']:
                    report['metrics'][metric.metric_name] = []
                report['metrics'][metric.metric_name].append({
                    'timestamp': metric.timestamp.isoformat(),
                    'value': metric.metric_value,
                    'details': eval(metric.details) if metric.details else {}
                })

            return report
        except Exception as e:
            logger.error(f"Error generating analytics report: {str(e)}")
            return {} 