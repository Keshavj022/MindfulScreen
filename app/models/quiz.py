from datetime import datetime
from app import db

class QuizResponse(db.Model):
    __tablename__ = 'quiz_responses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.String(50), nullable=False)
    answer = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
