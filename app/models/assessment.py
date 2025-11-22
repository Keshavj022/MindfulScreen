"""
Periodic Assessment Model - Weekly/Monthly wellness check-ins
"""
from datetime import datetime
from app import db
import json


class PeriodicAssessment(db.Model):
    """Stores weekly/monthly assessment results for tracking progress"""
    __tablename__ = 'periodic_assessments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Assessment type: 'weekly' or 'monthly'
    assessment_type = db.Column(db.String(20), nullable=False)

    # Period info (e.g., "2025-W47" for week 47 of 2025, "2025-11" for November 2025)
    period_key = db.Column(db.String(20), nullable=False)

    # Scores (0-100 scale)
    mental_wellness_score = db.Column(db.Float)
    stress_level_score = db.Column(db.Float)
    energy_score = db.Column(db.Float)
    sleep_quality_score = db.Column(db.Float)
    digital_wellness_score = db.Column(db.Float)
    productivity_score = db.Column(db.Float)
    mood_score = db.Column(db.Float)

    # Overall wellness index
    overall_wellness = db.Column(db.Float)

    # Big Five changes (JSON: trait -> score)
    big_five_snapshot = db.Column(db.Text)

    # Detailed responses (JSON)
    responses_json = db.Column(db.Text)

    # AI-generated insights
    insights = db.Column(db.Text)
    recommendations = db.Column(db.Text)

    # Comparison to previous period
    improvement_score = db.Column(db.Float)  # Positive = improved, Negative = declined

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref=db.backref('periodic_assessments', lazy='dynamic'))

    def set_big_five(self, scores):
        """Store Big Five scores as JSON"""
        self.big_five_snapshot = json.dumps(scores)

    def get_big_five(self):
        """Retrieve Big Five scores"""
        if self.big_five_snapshot:
            return json.loads(self.big_five_snapshot)
        return {}

    def set_responses(self, responses):
        """Store detailed responses as JSON"""
        self.responses_json = json.dumps(responses)

    def get_responses(self):
        """Retrieve responses"""
        if self.responses_json:
            return json.loads(self.responses_json)
        return {}

    def set_insights(self, insights_list):
        """Store insights as JSON"""
        self.insights = json.dumps(insights_list)

    def get_insights(self):
        """Retrieve insights"""
        if self.insights:
            return json.loads(self.insights)
        return []

    def set_recommendations(self, recs_list):
        """Store recommendations as JSON"""
        self.recommendations = json.dumps(recs_list)

    def get_recommendations(self):
        """Retrieve recommendations"""
        if self.recommendations:
            return json.loads(self.recommendations)
        return []

    @staticmethod
    def get_current_week_key():
        """Get current week key in format YYYY-WNN"""
        now = datetime.utcnow()
        return now.strftime('%Y-W%V')

    @staticmethod
    def get_current_month_key():
        """Get current month key in format YYYY-MM"""
        now = datetime.utcnow()
        return now.strftime('%Y-%m')

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'assessment_type': self.assessment_type,
            'period_key': self.period_key,
            'mental_wellness_score': self.mental_wellness_score,
            'stress_level_score': self.stress_level_score,
            'energy_score': self.energy_score,
            'sleep_quality_score': self.sleep_quality_score,
            'digital_wellness_score': self.digital_wellness_score,
            'productivity_score': self.productivity_score,
            'mood_score': self.mood_score,
            'overall_wellness': self.overall_wellness,
            'big_five': self.get_big_five(),
            'insights': self.get_insights(),
            'recommendations': self.get_recommendations(),
            'improvement_score': self.improvement_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


# Weekly assessment questions (quick check-in)
WEEKLY_QUESTIONS = [
    {'id': 'W1', 'text': 'How would you rate your overall mood this week?', 'category': 'mood'},
    {'id': 'W2', 'text': 'How well did you sleep this week?', 'category': 'sleep'},
    {'id': 'W3', 'text': 'How stressed did you feel this week?', 'category': 'stress'},
    {'id': 'W4', 'text': 'How productive were you this week?', 'category': 'productivity'},
    {'id': 'W5', 'text': 'How much energy did you have this week?', 'category': 'energy'},
    {'id': 'W6', 'text': 'How well did you manage your screen time this week?', 'category': 'digital'},
    {'id': 'W7', 'text': 'How connected did you feel to others this week?', 'category': 'social'},
    {'id': 'W8', 'text': 'How satisfied are you with this week overall?', 'category': 'satisfaction'},
]

# Monthly assessment questions (deeper reflection)
MONTHLY_QUESTIONS = [
    {'id': 'M1', 'text': 'How would you rate your mental wellness this month?', 'category': 'mental_wellness'},
    {'id': 'M2', 'text': 'How consistent was your sleep routine?', 'category': 'sleep'},
    {'id': 'M3', 'text': 'How well did you handle stress this month?', 'category': 'stress'},
    {'id': 'M4', 'text': 'How would you rate your work-life balance?', 'category': 'balance'},
    {'id': 'M5', 'text': 'How much progress did you make on personal goals?', 'category': 'goals'},
    {'id': 'M6', 'text': 'How healthy were your digital habits?', 'category': 'digital'},
    {'id': 'M7', 'text': 'How often did you practice self-care?', 'category': 'selfcare'},
    {'id': 'M8', 'text': 'How optimistic do you feel about next month?', 'category': 'outlook'},
    {'id': 'M9', 'text': 'How would you rate your physical activity level?', 'category': 'physical'},
    {'id': 'M10', 'text': 'Overall, how satisfied are you with this month?', 'category': 'satisfaction'},
]
