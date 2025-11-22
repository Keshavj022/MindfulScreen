from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models import ScreenSession, FrameAnalysis
from app.services.analytics import AnalyticsService
from app.services.knowledge_graph import KnowledgeGraphService
from app.services.ai_insights import AIInsightsService
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    return render_template('dashboard/dashboard.html')

@bp.route('/insights')
@login_required
def insights():
    return render_template('dashboard/insights.html')

@bp.route('/progress')
@login_required
def progress():
    return render_template('dashboard/progress.html')

@bp.route('/api/stats')
@login_required
def get_stats():
    analytics = AnalyticsService()
    return jsonify(analytics.get_user_stats(current_user.id))

@bp.route('/api/app-usage')
@login_required
def get_app_usage():
    analytics = AnalyticsService()
    return jsonify(analytics.get_app_usage_stats(current_user.id))

@bp.route('/api/content-analysis')
@login_required
def get_content_analysis():
    analytics = AnalyticsService()
    return jsonify(analytics.get_content_analysis(current_user.id))

@bp.route('/api/sentiment-timeline')
@login_required
def get_sentiment_timeline():
    analytics = AnalyticsService()
    return jsonify(analytics.get_sentiment_timeline(current_user.id))

@bp.route('/api/wellness-trends')
@login_required
def get_wellness_trends():
    analytics = AnalyticsService()
    return jsonify(analytics.get_wellness_trends(current_user.id))

@bp.route('/api/knowledge-graph')
@login_required
def get_knowledge_graph():
    kg_service = KnowledgeGraphService()
    graph_data = kg_service.get_user_graph(current_user.id)
    return jsonify(graph_data)

@bp.route('/api/app-details/<app_name>')
@login_required
def get_app_details(app_name):
    analytics = AnalyticsService()
    return jsonify(analytics.get_app_detailed_analysis(current_user.id, app_name))

@bp.route('/api/ai-insights')
@login_required
def get_ai_insights():
    """Get comprehensive AI-powered insights for the user"""
    insights_service = AIInsightsService()
    insights = insights_service.get_comprehensive_insights(current_user.id)
    return jsonify(insights)

@bp.route('/api/quick-insights')
@login_required
def get_quick_insights():
    """Get quick insights for dashboard display"""
    insights_service = AIInsightsService()
    insights = insights_service.get_quick_insights(current_user.id)
    return jsonify(insights)

@bp.route('/api/wellness-alerts')
@login_required
def get_wellness_alerts():
    """Get wellness alerts for the user"""
    insights_service = AIInsightsService()
    alerts = insights_service.get_wellness_alerts(current_user.id)
    return jsonify(alerts)

@bp.route('/api/recent-sessions')
@login_required
def get_recent_sessions():
    """Get recent sessions for the dashboard"""
    sessions = ScreenSession.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(ScreenSession.created_at.desc()).limit(10).all()

    return jsonify([{
        'id': s.id,
        'name': s.session_name,
        'created_at': s.created_at.isoformat(),
        'duration_seconds': s.duration_seconds,
        'wellness_score': s.wellness_score,
        'productivity_score': s.productivity_score,
        'top_app': max(s.app_usage.items(), key=lambda x: x[1])[0] if s.app_usage else 'Unknown'
    } for s in sessions])
