from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    location = db.Column(db.String(100))

    quiz_completed = db.Column(db.Boolean, default=False)
    personality_type = db.Column(db.String(50))
    personality_description = db.Column(db.Text)
    big_five_scores = db.Column(db.JSON)
    big_five_normalized = db.Column(db.JSON)
    personality_cluster = db.Column(db.Integer)
    cluster_confidence = db.Column(db.Float)
    strengths = db.Column(db.JSON)
    growth_areas = db.Column(db.JSON)
    stress_level = db.Column(db.String(20))
    wellness_goals = db.Column(db.JSON)

    # Mental Health Tracking
    mental_health_scores = db.Column(db.JSON)
    mental_wellness_index = db.Column(db.Float)
    mental_health_status = db.Column(db.String(50))
    mental_health_recommendations = db.Column(db.JSON)

    # Digital Wellness Tracking
    digital_wellness_index = db.Column(db.Float)
    digital_wellness_risk = db.Column(db.String(20))
    digital_wellness_scores = db.Column(db.JSON)

    # Progress Tracking
    wellness_history = db.Column(db.JSON)  # Historical wellness scores
    last_assessment_date = db.Column(db.DateTime)

    # Account verification and consent
    email_verified = db.Column(db.Boolean, default=False)
    terms_accepted_at = db.Column(db.DateTime)
    privacy_accepted_at = db.Column(db.DateTime)
    marketing_consent = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    quiz_responses = db.relationship('QuizResponse', backref='user', lazy=True, cascade='all, delete-orphan')
    screen_sessions = db.relationship('ScreenSession', backref='user', lazy=True, cascade='all, delete-orphan')
    knowledge_graph = db.relationship('KnowledgeGraph', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
