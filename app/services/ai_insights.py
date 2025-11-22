import json
from datetime import datetime, timedelta
from openai import OpenAI
from app.models import User, ScreenSession, FrameAnalysis
from config import Config

class AIInsightsService:
    """
    AI-powered insights service that provides personalized recommendations
    for digital and physical/mental wellbeing based on user's screen time data.
    """

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def get_comprehensive_insights(self, user_id):
        """Generate comprehensive AI insights for a user"""
        user = User.query.get(user_id)
        if not user:
            return None

        # Gather user data
        user_data = self._gather_user_data(user_id)

        if not user_data['has_data']:
            return self._get_new_user_insights(user)

        # Generate insights using AI
        insights = self._generate_ai_insights(user, user_data)

        return insights

    def _gather_user_data(self, user_id):
        """Gather comprehensive user data for analysis"""
        sessions = ScreenSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(ScreenSession.created_at.desc()).all()

        if not sessions:
            return {'has_data': False}

        # Calculate metrics
        total_duration = sum(s.duration_seconds or 0 for s in sessions)
        avg_wellness = sum(s.wellness_score or 0 for s in sessions) / len(sessions) if sessions else 0
        avg_productivity = sum(s.productivity_score or 0 for s in sessions) / len(sessions) if sessions else 0

        # App usage aggregation
        app_usage = {}
        content_categories = {}
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0, 'mixed': 0}
        wellness_impacts = {'positive': 0, 'negative': 0, 'neutral': 0}

        for session in sessions:
            if session.app_usage:
                for app, count in session.app_usage.items():
                    app_usage[app] = app_usage.get(app, 0) + count

            if session.content_categories:
                for cat, count in session.content_categories.items():
                    content_categories[cat] = content_categories.get(cat, 0) + count

            if session.sentiment_distribution:
                for sent, count in session.sentiment_distribution.items():
                    sentiment_counts[sent] = sentiment_counts.get(sent, 0) + count

        # Calculate frame-level wellness impacts
        for session in sessions[:10]:  # Last 10 sessions
            frames = FrameAnalysis.query.filter_by(session_id=session.id).all()
            for frame in frames:
                if frame.wellness_impact:
                    wellness_impacts[frame.wellness_impact] = wellness_impacts.get(frame.wellness_impact, 0) + 1

        # Calculate percentages
        total_frames = sum(wellness_impacts.values())
        high_risk_percentage = (wellness_impacts.get('negative', 0) / total_frames * 100) if total_frames > 0 else 0
        productive_percentage = (wellness_impacts.get('positive', 0) / total_frames * 100) if total_frames > 0 else 0

        # Sort apps by usage
        top_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        top_categories = sorted(content_categories.items(), key=lambda x: x[1], reverse=True)

        # Recent trend analysis
        recent_sessions = sessions[:5]
        older_sessions = sessions[5:10] if len(sessions) > 5 else []

        wellness_trend = 'stable'
        if recent_sessions and older_sessions:
            recent_avg = sum(s.wellness_score or 0 for s in recent_sessions) / len(recent_sessions)
            older_avg = sum(s.wellness_score or 0 for s in older_sessions) / len(older_sessions)
            if recent_avg > older_avg + 0.5:
                wellness_trend = 'improving'
            elif recent_avg < older_avg - 0.5:
                wellness_trend = 'declining'

        return {
            'has_data': True,
            'total_sessions': len(sessions),
            'total_duration_hours': round(total_duration / 3600, 1),
            'avg_wellness': round(avg_wellness, 1),
            'avg_productivity': round(avg_productivity, 1),
            'top_apps': top_apps,
            'content_categories': top_categories,
            'sentiment_distribution': sentiment_counts,
            'high_risk_percentage': round(high_risk_percentage, 1),
            'productive_percentage': round(productive_percentage, 1),
            'wellness_trend': wellness_trend,
            'wellness_impacts': wellness_impacts
        }

    def _generate_ai_insights(self, user, user_data):
        """Generate personalized AI insights using GPT-4"""

        # Prepare user context with enhanced personality data
        big_five = user.big_five_scores or {}
        mental_scores = user.mental_health_scores or {}
        strengths = user.strengths or []
        growth_areas = user.growth_areas or []

        user_context = f"""
User Profile:
- Name: {user.name}
- Age: {user.age or 'Unknown'}
- Occupation: {user.occupation or 'Unknown'}
- Personality Type: {user.personality_type or 'Unknown'}
- Personality Description: {user.personality_description or 'Not assessed'}
- Stress Level: {user.stress_level or 'Unknown'}
- Wellness Goals: {', '.join(user.wellness_goals) if user.wellness_goals else 'Not set'}

Big Five Personality Traits (1-5 scale):
- Openness: {big_five.get('openness', 'N/A')}
- Conscientiousness: {big_five.get('conscientiousness', 'N/A')}
- Extraversion: {big_five.get('extraversion', 'N/A')}
- Agreeableness: {big_five.get('agreeableness', 'N/A')}
- Neuroticism: {big_five.get('neuroticism', 'N/A')}

Strengths: {', '.join(strengths) if strengths else 'Not identified'}
Growth Areas: {', '.join(growth_areas) if growth_areas else 'Not identified'}

Mental Wellness Index: {user.mental_wellness_index or 'N/A'}/100
Mental Health Status: {user.mental_health_status or 'Unknown'}
Mental Health Category Scores:
- Depression indicators: {mental_scores.get('depression', 'N/A')}
- Anxiety indicators: {mental_scores.get('anxiety', 'N/A')}
- Stress indicators: {mental_scores.get('stress', 'N/A')}
- Sleep quality: {mental_scores.get('sleep', 'N/A')}
- Social support: {mental_scores.get('social_support', 'N/A')}
- Energy levels: {mental_scores.get('energy', 'N/A')}

Digital Wellness Index: {user.digital_wellness_index or 'N/A'}/100
Digital Risk Level: {user.digital_wellness_risk or 'Unknown'}

Screen Time Data:
- Total Sessions Analyzed: {user_data['total_sessions']}
- Total Time Analyzed: {user_data['total_duration_hours']} hours
- Average Wellness Score: {user_data['avg_wellness']}/10
- Average Productivity Score: {user_data['avg_productivity']}/10
- High-Risk Screen Time: {user_data['high_risk_percentage']}%
- Productive Screen Time: {user_data['productive_percentage']}%
- Wellness Trend: {user_data['wellness_trend']}

Top Applications Used:
{chr(10).join([f"- {app}: {count} frames" for app, count in user_data['top_apps'][:5]])}

Content Categories:
{chr(10).join([f"- {cat}: {count}" for cat, count in user_data['content_categories'][:5]])}

Sentiment Distribution:
- Positive: {user_data['sentiment_distribution']['positive']}
- Negative: {user_data['sentiment_distribution']['negative']}
- Neutral: {user_data['sentiment_distribution']['neutral']}
- Mixed: {user_data['sentiment_distribution']['mixed']}
"""

        prompt = f"""{user_context}

Based on this user's screen time data, personality profile, and mental health indicators, provide comprehensive, personalized insights as a caring friend, mentor, and wellness guide.

IMPORTANT: Tailor all advice to their specific personality type and mental health status:
- For high neuroticism: Focus on stress reduction and calming activities
- For low extraversion: Suggest solo wellness activities, not forced socializing
- For low conscientiousness: Provide simple, easy-to-follow routines
- For high openness: Include creative and novel wellness approaches
- Consider their mental health scores when suggesting activities (don't overwhelm someone showing anxiety signs)

Be specific, actionable, and supportive.

Generate insights in the following JSON format:
{{
    "overall_assessment": {{
        "summary": "2-3 sentence overall assessment of user's digital wellness",
        "wellness_grade": "A/B/C/D/F grade for digital wellness",
        "key_strength": "One main positive aspect",
        "primary_concern": "One main area needing attention"
    }},
    "digital_wellness_tips": [
        {{
            "title": "Short title",
            "description": "Detailed actionable advice",
            "priority": "high/medium/low",
            "category": "focus/reduce/balance/improve"
        }}
    ],
    "physical_health_tips": [
        {{
            "title": "Short title",
            "description": "Physical health advice related to screen time",
            "icon": "fa-icon-name"
        }}
    ],
    "mental_health_tips": [
        {{
            "title": "Short title",
            "description": "Mental health and mindfulness advice",
            "icon": "fa-icon-name"
        }}
    ],
    "productivity_suggestions": [
        {{
            "title": "Short title",
            "description": "How to be more productive based on their patterns",
            "expected_impact": "What improvement they can expect"
        }}
    ],
    "app_specific_advice": [
        {{
            "app_name": "App name from their usage",
            "current_usage": "Their usage pattern",
            "recommendation": "Specific advice for this app",
            "alternative": "Better alternative if applicable"
        }}
    ],
    "daily_routine_suggestions": {{
        "morning": "Morning routine advice",
        "work_hours": "During work/productive hours",
        "evening": "Evening wind-down advice",
        "before_bed": "Pre-sleep screen time advice"
    }},
    "weekly_challenges": [
        {{
            "challenge": "A specific weekly challenge",
            "goal": "What to achieve",
            "difficulty": "easy/medium/hard"
        }}
    ],
    "motivational_message": "A personalized, encouraging message for the user",
    "focus_areas": ["Area 1", "Area 2", "Area 3"],
    "avoid_areas": ["Thing to avoid 1", "Thing to avoid 2"],
    "wellness_score_prediction": {{
        "current": {user_data['avg_wellness']},
        "potential": "Score they could achieve with improvements",
        "timeframe": "How long to see improvements"
    }}
}}

Provide at least 3-5 items for each list category. Be specific to their actual usage patterns and apps."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a compassionate digital wellness expert and life coach. Provide personalized, actionable advice that helps users improve their digital habits, physical health, and mental wellbeing. Be supportive but honest about areas needing improvement."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=3000,
                temperature=0.7
            )

            content = response.choices[0].message.content

            # Parse JSON response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]

            insights = json.loads(content.strip())
            insights['user_data'] = user_data
            insights['generated_at'] = datetime.utcnow().isoformat()

            return insights

        except Exception as e:
            print(f"AI Insights generation error: {e}")
            return self._get_fallback_insights(user, user_data)

    def _get_new_user_insights(self, user):
        """Insights for new users with no data"""
        return {
            'overall_assessment': {
                'summary': f"Welcome to MindfulScreen, {user.name}! Start your digital wellness journey by recording your first screen analysis session.",
                'wellness_grade': 'N/A',
                'key_strength': 'Taking the first step towards digital wellness',
                'primary_concern': 'No data yet - start analyzing your screen time'
            },
            'digital_wellness_tips': [
                {
                    'title': 'Start Your First Analysis',
                    'description': 'Record a 5-10 minute screen session to begin tracking your digital habits.',
                    'priority': 'high',
                    'category': 'improve'
                },
                {
                    'title': 'Set Your Wellness Goals',
                    'description': 'Visit your profile to set personal wellness goals for better tracking.',
                    'priority': 'medium',
                    'category': 'focus'
                }
            ],
            'physical_health_tips': [
                {
                    'title': '20-20-20 Rule',
                    'description': 'Every 20 minutes, look at something 20 feet away for 20 seconds.',
                    'icon': 'fa-eye'
                }
            ],
            'mental_health_tips': [
                {
                    'title': 'Mindful Screen Use',
                    'description': 'Before picking up your phone, ask yourself: "What am I looking for?"',
                    'icon': 'fa-brain'
                }
            ],
            'motivational_message': "Every journey begins with a single step. You're already on the path to better digital wellness!",
            'is_new_user': True
        }

    def _get_fallback_insights(self, user, user_data):
        """Fallback insights if AI generation fails"""
        return {
            'overall_assessment': {
                'summary': f"Based on {user_data['total_sessions']} sessions, your digital wellness score is {user_data['avg_wellness']}/10.",
                'wellness_grade': 'B' if user_data['avg_wellness'] >= 6 else 'C',
                'key_strength': 'Consistent tracking of screen time',
                'primary_concern': 'Consider reducing high-risk screen time'
            },
            'digital_wellness_tips': [
                {
                    'title': 'Balance Your Screen Time',
                    'description': f"Your high-risk screen time is {user_data['high_risk_percentage']}%. Try to keep it under 20%.",
                    'priority': 'high',
                    'category': 'reduce'
                }
            ],
            'physical_health_tips': [
                {
                    'title': 'Take Regular Breaks',
                    'description': 'Stand up and stretch every 30 minutes of screen time.',
                    'icon': 'fa-walking'
                }
            ],
            'mental_health_tips': [
                {
                    'title': 'Digital Detox',
                    'description': 'Try a 1-hour digital detox each day to reset your mind.',
                    'icon': 'fa-spa'
                }
            ],
            'motivational_message': 'Keep tracking your screen time - awareness is the first step to improvement!',
            'user_data': user_data
        }

    def get_quick_insights(self, user_id, limit=3):
        """Get quick insights for dashboard display"""
        user_data = self._gather_user_data(user_id)

        if not user_data['has_data']:
            return [
                {
                    'type': 'info',
                    'icon': 'fa-info-circle',
                    'title': 'Get Started',
                    'message': 'Start your first analysis session to get personalized insights.'
                }
            ]

        insights = []

        # Wellness trend insight
        if user_data['wellness_trend'] == 'improving':
            insights.append({
                'type': 'success',
                'icon': 'fa-arrow-up',
                'title': 'Wellness Improving',
                'message': 'Great job! Your wellness score is trending upward.'
            })
        elif user_data['wellness_trend'] == 'declining':
            insights.append({
                'type': 'warning',
                'icon': 'fa-arrow-down',
                'title': 'Wellness Declining',
                'message': 'Your wellness score has dropped. Consider reducing social media time.'
            })

        # High-risk time insight
        if user_data['high_risk_percentage'] > 30:
            insights.append({
                'type': 'danger',
                'icon': 'fa-exclamation-triangle',
                'title': 'High-Risk Alert',
                'message': f"{user_data['high_risk_percentage']}% of your screen time is high-risk. Try healthier alternatives."
            })

        # Productive time insight
        if user_data['productive_percentage'] > 50:
            insights.append({
                'type': 'success',
                'icon': 'fa-star',
                'title': 'Productive User',
                'message': f"Excellent! {user_data['productive_percentage']}% of your screen time is productive."
            })
        elif user_data['productive_percentage'] < 20:
            insights.append({
                'type': 'info',
                'icon': 'fa-lightbulb',
                'title': 'Boost Productivity',
                'message': 'Try using more educational and work-related apps to boost productivity.'
            })

        # Top app insight
        if user_data['top_apps']:
            top_app = user_data['top_apps'][0][0]
            social_apps = ['instagram', 'facebook', 'twitter', 'tiktok', 'snapchat', 'reddit']
            if any(s in top_app.lower() for s in social_apps):
                insights.append({
                    'type': 'warning',
                    'icon': 'fa-mobile-alt',
                    'title': f'Most Used: {top_app}',
                    'message': 'Social media is your top app. Consider setting usage limits.'
                })

        return insights[:limit]

    def get_wellness_alerts(self, user_id):
        """Get wellness alerts for the user"""
        user_data = self._gather_user_data(user_id)
        alerts = []

        if not user_data['has_data']:
            return alerts

        # High negative sentiment
        total_sentiment = sum(user_data['sentiment_distribution'].values())
        if total_sentiment > 0:
            negative_ratio = user_data['sentiment_distribution']['negative'] / total_sentiment
            if negative_ratio > 0.3:
                alerts.append({
                    'type': 'warning',
                    'message': 'High negative content exposure detected. Consider curating your feeds.'
                })

        # Too much screen time
        if user_data['total_duration_hours'] > 50:
            alerts.append({
                'type': 'danger',
                'message': 'Extended screen time detected. Remember to take breaks and rest your eyes.'
            })

        # Low wellness score
        if user_data['avg_wellness'] < 4:
            alerts.append({
                'type': 'warning',
                'message': 'Your wellness score is below average. Review your AI insights for improvement tips.'
            })

        return alerts
