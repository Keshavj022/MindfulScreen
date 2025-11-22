"""
Demo Data Generator for MindfulScreen
Creates comprehensive showcase data for demo@mindfulscreen.com
"""
from app import db
from app.models import User, QuizResponse, ScreenSession, FrameAnalysis, KnowledgeGraph, PeriodicAssessment
from app.services.knowledge_graph import KnowledgeGraphService
from datetime import datetime, timedelta
import random
import json


def create_demo_user():
    """Create or update demo user with comprehensive profile data"""
    demo_user = User.query.filter_by(email='demo@mindfulscreen.com').first()

    if demo_user:
        # Update existing demo user with all showcase data
        update_demo_user_profile(demo_user)
        return demo_user

    demo_user = User(
        name='Demo User',
        email='demo@mindfulscreen.com',
        phone='+1-555-0123',
        age=28,
        gender='Male',
        occupation='Software Engineer',
        location='San Francisco, USA',
        quiz_completed=True,
        email_verified=True,
        terms_accepted_at=datetime.utcnow() - timedelta(days=90),
        privacy_accepted_at=datetime.utcnow() - timedelta(days=90),
        marketing_consent=True,

        # Personality data - "The Analytical Introvert"
        personality_type='The Analytical Introvert',
        personality_description='You prefer deep thinking and solitary activities. You have a rich inner world and excel at focused, detailed work.',
        personality_cluster=1,
        cluster_confidence=0.85,

        # Big Five scores (1-5 scale)
        big_five_scores={
            'openness': 4.2,
            'conscientiousness': 4.0,
            'extraversion': 2.8,
            'agreeableness': 3.8,
            'neuroticism': 2.5
        },

        # Normalized Big Five (0-1 scale)
        big_five_normalized=json.dumps({
            'openness': 0.80,
            'conscientiousness': 0.75,
            'extraversion': 0.45,
            'agreeableness': 0.70,
            'neuroticism': 0.38
        }),

        # Strengths and growth areas
        strengths=json.dumps(['Deep thinking', 'Focus', 'Independence', 'Attention to detail', 'Problem solving']),
        growth_areas=json.dumps(['Social engagement', 'Sharing ideas openly', 'Taking breaks']),

        # Mental health data
        mental_health_scores=json.dumps({
            'depression': 1.8,
            'anxiety': 2.2,
            'stress': 2.5,
            'sleep': 4.0,
            'energy': 3.8
        }),
        mental_wellness_index=72.5,
        mental_health_status='good',
        mental_health_recommendations=json.dumps([
            {'area': 'Work-Life Balance', 'priority': 'medium', 'tip': 'Schedule regular breaks during focused work sessions.'},
            {'area': 'Social Connection', 'priority': 'low', 'tip': 'Your introversion is healthy, but maintain meaningful connections.'}
        ]),

        # Digital wellness
        digital_wellness_index=68.0,
        digital_wellness_risk='low',
        digital_wellness_scores=json.dumps({
            'digital_impact': 2,
            'digital_dependency': 3,
            'comparison': 2,
            'sleep_impact': 2
        }),

        # Wellness goals
        stress_level='low',
        wellness_goals=[
            'Reduce screen time before bed',
            'Take more breaks during work',
            'Maintain work-life balance'
        ],

        # Wellness history (for progress tracking)
        wellness_history=json.dumps([
            {'date': (datetime.utcnow() - timedelta(days=84)).isoformat(), 'score': 58.0},
            {'date': (datetime.utcnow() - timedelta(days=70)).isoformat(), 'score': 62.5},
            {'date': (datetime.utcnow() - timedelta(days=56)).isoformat(), 'score': 64.0},
            {'date': (datetime.utcnow() - timedelta(days=42)).isoformat(), 'score': 67.5},
            {'date': (datetime.utcnow() - timedelta(days=28)).isoformat(), 'score': 69.0},
            {'date': (datetime.utcnow() - timedelta(days=14)).isoformat(), 'score': 71.0},
            {'date': datetime.utcnow().isoformat(), 'score': 72.5}
        ]),

        last_assessment_date=datetime.utcnow() - timedelta(days=3)
    )
    demo_user.set_password('Demo@123')  # Strong password

    db.session.add(demo_user)
    db.session.commit()

    # Create all related data
    create_quiz_responses(demo_user.id)
    create_demo_sessions(demo_user.id)
    create_weekly_assessments(demo_user.id)
    create_monthly_assessments(demo_user.id)

    # Build knowledge graph
    try:
        kg_service = KnowledgeGraphService()
        kg_service.create_or_update_graph(demo_user.id)
    except Exception as e:
        print(f'Knowledge graph creation skipped: {e}')

    return demo_user


def update_demo_user_profile(user):
    """Update existing demo user with full profile data"""
    user.personality_type = 'The Analytical Introvert'
    user.personality_description = 'You prefer deep thinking and solitary activities. You have a rich inner world and excel at focused, detailed work.'
    user.personality_cluster = 1
    user.cluster_confidence = 0.85
    user.quiz_completed = True
    user.email_verified = True

    user.big_five_scores = {
        'openness': 4.2,
        'conscientiousness': 4.0,
        'extraversion': 2.8,
        'agreeableness': 3.8,
        'neuroticism': 2.5
    }

    user.big_five_normalized = json.dumps({
        'openness': 0.80,
        'conscientiousness': 0.75,
        'extraversion': 0.45,
        'agreeableness': 0.70,
        'neuroticism': 0.38
    })

    user.strengths = json.dumps(['Deep thinking', 'Focus', 'Independence', 'Attention to detail'])
    user.growth_areas = json.dumps(['Social engagement', 'Sharing ideas openly', 'Taking breaks'])

    user.mental_wellness_index = 72.5
    user.mental_health_status = 'good'
    user.digital_wellness_index = 68.0
    user.digital_wellness_risk = 'low'
    user.stress_level = 'low'

    user.wellness_history = json.dumps([
        {'date': (datetime.utcnow() - timedelta(days=84)).isoformat(), 'score': 58.0},
        {'date': (datetime.utcnow() - timedelta(days=70)).isoformat(), 'score': 62.5},
        {'date': (datetime.utcnow() - timedelta(days=56)).isoformat(), 'score': 64.0},
        {'date': (datetime.utcnow() - timedelta(days=42)).isoformat(), 'score': 67.5},
        {'date': (datetime.utcnow() - timedelta(days=28)).isoformat(), 'score': 69.0},
        {'date': (datetime.utcnow() - timedelta(days=14)).isoformat(), 'score': 71.0},
        {'date': datetime.utcnow().isoformat(), 'score': 72.5}
    ])

    db.session.commit()


def create_quiz_responses(user_id):
    """Create quiz responses for the shortened quiz (35 questions)"""
    # Clear existing responses
    QuizResponse.query.filter_by(user_id=user_id).delete()

    # Big Five responses (25 questions - 5 per trait)
    big_five_responses = {
        # Extraversion (moderate-low)
        'EXT1': 2, 'EXT2': 3, 'EXT3': 3, 'EXT4': 4, 'EXT5': 4,
        # Neuroticism (low)
        'EST1': 2, 'EST2': 4, 'EST3': 2, 'EST4': 2, 'EST5': 2,
        # Agreeableness (high)
        'AGR1': 4, 'AGR2': 4, 'AGR3': 5, 'AGR4': 2, 'AGR5': 4,
        # Conscientiousness (high)
        'CSN1': 4, 'CSN2': 4, 'CSN3': 3, 'CSN4': 2, 'CSN5': 4,
        # Openness (high)
        'OPN1': 5, 'OPN2': 4, 'OPN3': 5, 'OPN4': 4, 'OPN5': 2,
    }

    # Mental health responses (5 questions)
    mental_health_responses = {
        'MH1': 2, 'MH2': 2, 'MH3': 4, 'MH4': 3, 'MH5': 4
    }

    # Digital wellness responses (5 questions)
    wellness_responses = {
        'DW1': 2, 'DW2': 3, 'DW3': 2, 'DW4': 2, 'DW5': 4
    }

    all_responses = {**big_five_responses, **mental_health_responses, **wellness_responses}

    for q_id, answer in all_responses.items():
        qr = QuizResponse(user_id=user_id, question_id=q_id, answer=answer)
        db.session.add(qr)

    db.session.commit()


def create_demo_sessions(user_id):
    """Create realistic screen sessions with improvement over time"""
    apps = ['VSCode', 'Chrome', 'Slack', 'YouTube', 'LinkedIn', 'Terminal', 'Notion', 'Spotify']
    productive_apps = ['VSCode', 'Terminal', 'Notion', 'Chrome']
    content_types = ['work', 'educational', 'social_media', 'entertainment', 'communication']
    sentiments = ['positive', 'negative', 'neutral', 'mixed']

    # Clear existing sessions
    ScreenSession.query.filter_by(user_id=user_id).delete()

    # Create 14 days of sessions with improving wellness scores
    for i in range(14):
        date_offset = datetime.utcnow() - timedelta(days=13-i)

        # Wellness improves over time
        base_wellness = 5.5 + (i * 0.15)  # Starts at 5.5, improves to ~7.5
        base_productivity = 6.0 + (i * 0.12)

        num_sessions = random.randint(1, 3)

        for s in range(num_sessions):
            session = ScreenSession(
                user_id=user_id,
                session_name=f'Work Session {i*3+s+1}',
                duration_seconds=random.randint(1800, 7200),
                total_frames=random.randint(40, 180),
                wellness_score=round(base_wellness + random.uniform(-0.5, 0.5), 2),
                productivity_score=round(base_productivity + random.uniform(-0.5, 0.5), 2),
                sentiment_distribution={
                    'positive': random.randint(30, 50),
                    'negative': random.randint(5, 20),
                    'neutral': random.randint(25, 45),
                    'mixed': random.randint(5, 15)
                },
                app_usage={
                    random.choice(productive_apps): random.randint(30, 50),
                    random.choice(apps): random.randint(15, 35),
                    random.choice(apps): random.randint(10, 25),
                    random.choice(apps): random.randint(5, 20)
                },
                content_categories={
                    'work': random.randint(35, 55),
                    'educational': random.randint(15, 30),
                    random.choice(['social_media', 'entertainment', 'communication']): random.randint(10, 25)
                },
                status='completed',
                created_at=date_offset + timedelta(hours=random.randint(9, 18))
            )

            db.session.add(session)
            db.session.flush()

            # Create frame analyses
            for j in range(random.randint(25, 60)):
                frame = FrameAnalysis(
                    session_id=session.id,
                    frame_number=j + 1,
                    timestamp=j * 2.0,
                    frame_path=f'/data/frames/demo/session_{session.id}/frame_{j}.jpg',
                    app_detected=random.choice(apps),
                    content_type=random.choice(content_types),
                    extracted_text=f'Code review in progress...' if j % 3 == 0 else f'Reading documentation...',
                    detected_language='en',
                    sentiment=random.choice(sentiments),
                    sentiment_score=round(random.uniform(-0.3, 0.8), 2),
                    objects_detected=['text', 'code', 'ui_elements'],
                    content_description=f'Developer working on code review and documentation',
                    wellness_impact=random.choices(['positive', 'neutral', 'negative'], weights=[50, 40, 10])[0]
                )
                db.session.add(frame)

    db.session.commit()


def create_weekly_assessments(user_id):
    """Create 12 weeks of weekly assessments showing improvement"""
    # Clear existing weekly assessments
    PeriodicAssessment.query.filter_by(user_id=user_id, assessment_type='weekly').delete()

    base_date = datetime.utcnow() - timedelta(weeks=12)

    for week in range(12):
        week_date = base_date + timedelta(weeks=week)
        week_key = week_date.strftime('%Y-W%V')

        # Scores improve over time with some variance
        base_score = 55 + (week * 2)  # From 55 to ~77

        improvement = random.uniform(1, 5) if week > 0 else 0

        assessment = PeriodicAssessment(
            user_id=user_id,
            assessment_type='weekly',
            period_key=week_key,
            overall_wellness=min(85, base_score + random.uniform(-5, 5)),
            mood_score=min(90, base_score + random.uniform(-3, 8)),
            sleep_quality_score=min(85, base_score - 5 + random.uniform(-5, 10)),
            stress_level_score=max(20, 85 - base_score + random.uniform(-5, 5)),  # Inverted
            productivity_score=min(90, base_score + 5 + random.uniform(-3, 5)),
            energy_score=min(85, base_score + random.uniform(-5, 5)),
            digital_wellness_score=min(80, base_score - 5 + random.uniform(-3, 5)),
            improvement_score=improvement if week > 0 else None,
            created_at=week_date,
            completed_at=week_date + timedelta(hours=random.randint(1, 12))
        )

        # Add insights
        insights = []
        if assessment.overall_wellness > 70:
            insights.append("Great week! Your wellness scores are strong.")
        if assessment.productivity_score > 75:
            insights.append("Excellent productivity this week!")
        if assessment.stress_level_score < 40:
            insights.append("Low stress levels - good work-life balance.")
        if not insights:
            insights.append("Steady progress. Keep up your healthy routines.")

        assessment.set_insights(insights)

        # Add responses
        responses = {
            'W1': random.randint(3, 5),
            'W2': random.randint(3, 5),
            'W3': random.randint(2, 4),
            'W4': random.randint(3, 5),
            'W5': random.randint(3, 5),
            'W6': random.randint(3, 5),
            'W7': random.randint(3, 4),
            'W8': random.randint(3, 5)
        }
        assessment.set_responses(responses)

        db.session.add(assessment)

    db.session.commit()


def create_monthly_assessments(user_id):
    """Create 6 months of monthly assessments showing improvement"""
    # Clear existing monthly assessments
    PeriodicAssessment.query.filter_by(user_id=user_id, assessment_type='monthly').delete()

    base_date = datetime.utcnow() - timedelta(days=180)

    for month in range(6):
        month_date = base_date + timedelta(days=month * 30)
        month_key = month_date.strftime('%Y-%m')

        # Monthly scores show bigger picture improvement
        base_score = 52 + (month * 4)  # From 52 to ~72

        improvement = random.uniform(2, 6) if month > 0 else 0

        assessment = PeriodicAssessment(
            user_id=user_id,
            assessment_type='monthly',
            period_key=month_key,
            overall_wellness=min(82, base_score + random.uniform(-3, 5)),
            mental_wellness_score=min(80, base_score + random.uniform(-5, 5)),
            sleep_quality_score=min(78, base_score - 3 + random.uniform(-5, 8)),
            stress_level_score=min(80, base_score + random.uniform(-5, 5)),
            digital_wellness_score=min(75, base_score - 5 + random.uniform(-3, 5)),
            productivity_score=min(85, base_score + 3 + random.uniform(-3, 5)),
            improvement_score=improvement if month > 0 else None,
            created_at=month_date,
            completed_at=month_date + timedelta(hours=random.randint(1, 24))
        )

        # Big Five snapshot
        assessment.set_big_five({
            'openness': 0.78 + (month * 0.01),
            'conscientiousness': 0.73 + (month * 0.01),
            'extraversion': 0.44 + (month * 0.005),
            'agreeableness': 0.68 + (month * 0.01),
            'neuroticism': 0.40 - (month * 0.01)  # Decreasing is good
        })

        # Add insights
        insights = []
        if assessment.overall_wellness > 65:
            insights.append("Positive monthly trend in overall wellness.")
        if assessment.improvement_score and assessment.improvement_score > 3:
            insights.append("Great improvement from last month!")
        insights.append("Continue with your self-care routines.")

        assessment.set_insights(insights)

        # Add responses
        responses = {f'M{i}': random.randint(3, 5) for i in range(1, 11)}
        assessment.set_responses(responses)

        db.session.add(assessment)

    db.session.commit()


def initialize_demo_data():
    """Initialize all demo data"""
    try:
        demo_user = create_demo_user()
        print(f'Demo user created/updated: {demo_user.email}')
        print('Password: Demo@123')
        print(f'Personality: {demo_user.personality_type}')
        print(f'Wellness Index: {demo_user.mental_wellness_index}')
        return True
    except Exception as e:
        print(f'Error creating demo data: {e}')
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return False
