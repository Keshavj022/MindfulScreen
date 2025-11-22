from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db, csrf
from app.models import ScreenSession
from app.services.screen_analyzer import ScreenAnalyzerService
import json

bp = Blueprint('analyzer', __name__, url_prefix='/analyzer')

@bp.route('/')
@login_required
def index():
    return render_template('analyzer/analyzer.html')

@bp.route('/api/start-session', methods=['POST'])
@login_required
@csrf.exempt
def start_session():
    data = request.json
    session_name = data.get('session_name', f'Session {ScreenSession.query.filter_by(user_id=current_user.id).count() + 1}')

    session = ScreenSession(
        user_id=current_user.id,
        session_name=session_name,
        status='recording'
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({'success': True, 'session_id': session.id})

@bp.route('/api/upload-frame', methods=['POST'])
@login_required
@csrf.exempt
def upload_frame():
    session_id = request.form.get('session_id')
    frame_number = request.form.get('frame_number')
    timestamp = request.form.get('timestamp')
    frame_data = request.files.get('frame')
    audio_data = request.form.get('audio_text')

    session = ScreenSession.query.get(session_id)
    if not session or session.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Invalid session'}), 403

    analyzer = ScreenAnalyzerService()
    result = analyzer.analyze_frame(
        session_id=session_id,
        frame_number=int(frame_number),
        timestamp=float(timestamp),
        frame_data=frame_data,
        audio_text=audio_data
    )

    return jsonify({'success': True, 'analysis': result})

@bp.route('/api/complete-session/<int:session_id>', methods=['POST'])
@login_required
@csrf.exempt
def complete_session(session_id):
    session = ScreenSession.query.get(session_id)
    if not session or session.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Invalid session'}), 403

    analyzer = ScreenAnalyzerService()
    summary = analyzer.generate_session_summary(session_id)

    session.status = 'completed'
    session.total_frames = summary['total_frames']
    session.duration_seconds = summary['duration_seconds']
    session.wellness_score = summary['wellness_score']
    session.productivity_score = summary['productivity_score']
    session.sentiment_distribution = summary['sentiment_distribution']
    session.app_usage = summary['app_usage']
    session.content_categories = summary['content_categories']

    db.session.commit()

    from app.services.knowledge_graph import KnowledgeGraphService
    kg_service = KnowledgeGraphService()
    kg_service.update_user_graph(current_user.id)

    return jsonify({'success': True, 'summary': summary})

@bp.route('/api/sessions')
@login_required
def get_sessions():
    sessions = ScreenSession.query.filter_by(user_id=current_user.id).order_by(ScreenSession.created_at.desc()).all()
    return jsonify([{
        'id': s.id,
        'name': s.session_name,
        'created_at': s.created_at.isoformat(),
        'duration_seconds': s.duration_seconds,
        'wellness_score': s.wellness_score,
        'productivity_score': s.productivity_score,
        'status': s.status
    } for s in sessions])
