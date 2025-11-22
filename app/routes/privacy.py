from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import ScreenSession, FrameAnalysis, AuditLog
from pathlib import Path
import json
from datetime import datetime
import shutil

bp = Blueprint('privacy', __name__, url_prefix='/privacy')

@bp.route('/policy')
def policy():
    return render_template('privacy/policy.html')

@bp.route('/terms')
def terms():
    return render_template('privacy/terms.html')

@bp.route('/data-settings')
@login_required
def data_settings():
    return render_template('privacy/data_settings.html')

@bp.route('/export-data', methods=['POST'])
@login_required
def export_data():
    try:
        user_data = {
            'user_info': {
                'name': current_user.name,
                'email': current_user.email,
                'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
                'age': current_user.age,
                'gender': current_user.gender,
                'occupation': current_user.occupation,
                'location': current_user.location
            },
            'personality': {
                'type': current_user.personality_type,
                'big_five_scores': current_user.big_five_scores
            },
            'sessions': []
        }

        sessions = ScreenSession.query.filter_by(user_id=current_user.id).all()
        for session in sessions:
            user_data['sessions'].append({
                'id': session.id,
                'created_at': session.created_at.isoformat() if session.created_at else None,
                'duration': session.duration,
                'wellness_score': session.wellness_score,
                'productivity_score': session.productivity_score,
                'frame_count': session.frame_count
            })

        AuditLog.log_event(
            user_id=current_user.id,
            action='EXPORT',
            resource='user_data',
            status='success',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        return jsonify({
            'success': True,
            'data': user_data,
            'exported_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        AuditLog.log_event(
            user_id=current_user.id,
            action='EXPORT',
            resource='user_data',
            status='failure',
            ip_address=request.remote_addr,
            details={'error': str(e)}
        )
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    try:
        user_id = current_user.id

        FrameAnalysis.query.filter_by(session_id=ScreenSession.id).filter(
            ScreenSession.user_id == user_id
        ).delete(synchronize_session=False)

        ScreenSession.query.filter_by(user_id=user_id).delete()

        from app.models import QuizResponse
        QuizResponse.query.filter_by(user_id=user_id).delete()

        from app.models import KnowledgeGraph
        KnowledgeGraph.query.filter_by(user_id=user_id).delete()

        from app.models import UserConsent
        UserConsent.query.filter_by(user_id=user_id).delete()

        from flask_login import logout_user
        from app.models import User
        user = User.query.get(user_id)

        AuditLog.log_event(
            user_id=user_id,
            action='DELETE',
            resource='account',
            status='success',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        db.session.delete(user)
        db.session.commit()

        logout_user()

        flash('Your account and all associated data have been permanently deleted.', 'success')
        return redirect(url_for('auth.signup'))

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting your account. Please try again.', 'danger')
        return redirect(url_for('privacy.data_settings'))

@bp.route('/delete-sessions', methods=['POST'])
@login_required
def delete_sessions():
    try:
        sessions = ScreenSession.query.filter_by(user_id=current_user.id).all()

        for session in sessions:
            FrameAnalysis.query.filter_by(session_id=session.id).delete()

        ScreenSession.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        AuditLog.log_event(
            user_id=current_user.id,
            action='DELETE',
            resource='all_sessions',
            status='success',
            ip_address=request.remote_addr
        )

        return jsonify({'success': True, 'message': 'All session data deleted'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
