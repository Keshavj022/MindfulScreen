from datetime import datetime
from app import db

class ScreenSession(db.Model):
    __tablename__ = 'screen_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_name = db.Column(db.String(200))
    duration_seconds = db.Column(db.Integer)
    total_frames = db.Column(db.Integer)
    wellness_score = db.Column(db.Float)
    productivity_score = db.Column(db.Float)
    sentiment_distribution = db.Column(db.JSON)
    app_usage = db.Column(db.JSON)
    content_categories = db.Column(db.JSON)
    status = db.Column(db.String(20), default='processing')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    frames = db.relationship('FrameAnalysis', backref='session', lazy=True, cascade='all, delete-orphan')

class FrameAnalysis(db.Model):
    __tablename__ = 'frame_analysis'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('screen_sessions.id'), nullable=False)
    frame_number = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)
    frame_path = db.Column(db.String(500))
    app_detected = db.Column(db.String(100))
    content_type = db.Column(db.String(100))
    extracted_text = db.Column(db.Text)
    detected_language = db.Column(db.String(20))
    sentiment = db.Column(db.String(20))
    sentiment_score = db.Column(db.Float)
    objects_detected = db.Column(db.JSON)
    content_description = db.Column(db.Text)
    wellness_impact = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
