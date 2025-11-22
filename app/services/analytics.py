from app.models import ScreenSession, FrameAnalysis, User
from sqlalchemy import func
from datetime import datetime, timedelta

class AnalyticsService:
    def get_user_stats(self, user_id):
        sessions = ScreenSession.query.filter_by(user_id=user_id, status='completed').all()

        if not sessions:
            return {
                'total_sessions': 0,
                'total_duration': 0,
                'avg_wellness': None,
                'avg_productivity': None,
                'total_frames': 0,
                'no_data': True
            }

        total_duration = sum(s.duration_seconds or 0 for s in sessions)
        total_frames = sum(s.total_frames or 0 for s in sessions)
        avg_wellness = sum(s.wellness_score or 0 for s in sessions) / len(sessions)
        avg_productivity = sum(s.productivity_score or 0 for s in sessions) / len(sessions)

        return {
            'total_sessions': len(sessions),
            'total_duration': total_duration,
            'avg_wellness': round(avg_wellness, 2),
            'avg_productivity': round(avg_productivity, 2),
            'total_frames': total_frames
        }

    def get_app_usage_stats(self, user_id):
        sessions = ScreenSession.query.filter_by(user_id=user_id, status='completed').all()

        app_usage = {}
        for session in sessions:
            if session.app_usage:
                for app, count in session.app_usage.items():
                    app_usage[app] = app_usage.get(app, 0) + count

        total = sum(app_usage.values())
        return {
            'apps': [
                {
                    'name': app,
                    'count': count,
                    'percentage': round((count / total * 100), 1) if total > 0 else 0
                }
                for app, count in sorted(app_usage.items(), key=lambda x: x[1], reverse=True)
            ]
        }

    def get_content_analysis(self, user_id):
        sessions = ScreenSession.query.filter_by(user_id=user_id, status='completed').all()

        content_types = {}
        sentiment_data = {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}

        for session in sessions:
            if session.content_categories:
                for cat, count in session.content_categories.items():
                    content_types[cat] = content_types.get(cat, 0) + count

            if session.sentiment_distribution:
                for sent, count in session.sentiment_distribution.items():
                    sentiment_data[sent] = sentiment_data.get(sent, 0) + count

        return {
            'content_types': content_types,
            'sentiment_distribution': sentiment_data
        }

    def get_sentiment_timeline(self, user_id):
        sessions = ScreenSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(ScreenSession.created_at).all()

        timeline = []
        for session in sessions:
            if session.sentiment_distribution:
                total = sum(session.sentiment_distribution.values())
                timeline.append({
                    'date': session.created_at.strftime('%Y-%m-%d'),
                    'positive': session.sentiment_distribution.get('positive', 0) / total * 100 if total > 0 else 0,
                    'negative': session.sentiment_distribution.get('negative', 0) / total * 100 if total > 0 else 0,
                    'neutral': session.sentiment_distribution.get('neutral', 0) / total * 100 if total > 0 else 0
                })

        return timeline

    def get_wellness_trends(self, user_id):
        sessions = ScreenSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(ScreenSession.created_at).all()

        trends = []
        for session in sessions:
            trends.append({
                'date': session.created_at.strftime('%Y-%m-%d %H:%M'),
                'wellness_score': session.wellness_score or 5.0,
                'productivity_score': session.productivity_score or 5.0
            })

        return trends

    def get_app_detailed_analysis(self, user_id, app_name):
        frames = FrameAnalysis.query.join(ScreenSession).filter(
            ScreenSession.user_id == user_id,
            FrameAnalysis.app_detected == app_name
        ).all()

        if not frames:
            return {'error': 'No data found for this app'}

        content_types = {}
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}
        wellness_impacts = {'positive': 0, 'negative': 0, 'neutral': 0}

        for frame in frames:
            if frame.content_type:
                content_types[frame.content_type] = content_types.get(frame.content_type, 0) + 1
            sentiments[frame.sentiment] = sentiments.get(frame.sentiment, 0) + 1
            wellness_impacts[frame.wellness_impact] = wellness_impacts.get(frame.wellness_impact, 0) + 1

        total_frames = len(frames)
        avg_sentiment_score = sum(f.sentiment_score for f in frames if f.sentiment_score) / total_frames

        return {
            'app_name': app_name,
            'total_frames': total_frames,
            'content_types': content_types,
            'sentiments': sentiments,
            'wellness_impacts': wellness_impacts,
            'avg_sentiment_score': round(avg_sentiment_score, 2)
        }
