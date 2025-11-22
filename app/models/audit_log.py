from datetime import datetime
from app import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False)
    details = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.resource} by user {self.user_id}>'

    @staticmethod
    def log_event(user_id, action, resource, status, ip_address=None, user_agent=None, details=None):
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            details=details
        )
        db.session.add(log)
        db.session.commit()
        return log


class UserConsent(db.Model):
    __tablename__ = 'user_consents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    consent_type = db.Column(db.String(50), nullable=False)
    consent_version = db.Column(db.String(20), nullable=False)
    granted = db.Column(db.Boolean, default=False, nullable=False)
    granted_at = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('consents', lazy=True))

    def __repr__(self):
        return f'<UserConsent {self.consent_type} for user {self.user_id}>'
