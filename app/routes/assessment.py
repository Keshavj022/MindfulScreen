"""
Periodic Assessment Routes - Weekly/Monthly wellness check-ins
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import PeriodicAssessment, WEEKLY_QUESTIONS, MONTHLY_QUESTIONS
from datetime import datetime, timedelta
import json

bp = Blueprint('assessment', __name__, url_prefix='/assessment')


@bp.route('/weekly', methods=['GET', 'POST'])
@login_required
def weekly():
    """Weekly wellness check-in"""
    current_week = PeriodicAssessment.get_current_week_key()

    # Check if already completed this week
    existing = PeriodicAssessment.query.filter_by(
        user_id=current_user.id,
        assessment_type='weekly',
        period_key=current_week
    ).first()

    if request.method == 'POST':
        responses = {}
        total_score = 0

        for q in WEEKLY_QUESTIONS:
            value = request.form.get(q['id'], 3)
            responses[q['id']] = int(value)
            total_score += int(value)

        avg_score = (total_score / len(WEEKLY_QUESTIONS)) * 20  # Convert to 0-100

        # Get previous week's assessment for comparison
        prev_week = (datetime.utcnow() - timedelta(weeks=1)).strftime('%Y-W%V')
        prev_assessment = PeriodicAssessment.query.filter_by(
            user_id=current_user.id,
            assessment_type='weekly',
            period_key=prev_week
        ).first()

        improvement = 0
        if prev_assessment and prev_assessment.overall_wellness:
            improvement = avg_score - prev_assessment.overall_wellness

        # Create or update assessment
        if existing:
            assessment = existing
        else:
            assessment = PeriodicAssessment(
                user_id=current_user.id,
                assessment_type='weekly',
                period_key=current_week
            )

        assessment.overall_wellness = avg_score
        assessment.mood_score = responses.get('W1', 3) * 20
        assessment.sleep_quality_score = responses.get('W2', 3) * 20
        assessment.stress_level_score = 100 - (responses.get('W3', 3) * 20)  # Invert
        assessment.productivity_score = responses.get('W4', 3) * 20
        assessment.energy_score = responses.get('W5', 3) * 20
        assessment.digital_wellness_score = responses.get('W6', 3) * 20
        assessment.improvement_score = improvement
        assessment.set_responses(responses)
        assessment.completed_at = datetime.utcnow()

        # Generate insights
        insights = generate_weekly_insights(responses, improvement)
        assessment.set_insights(insights)

        db.session.add(assessment)
        db.session.commit()

        flash('Weekly check-in completed! Check your progress below.', 'success')
        return redirect(url_for('assessment.history'))

    return render_template('assessment/weekly.html',
                         questions=WEEKLY_QUESTIONS,
                         existing=existing)


@bp.route('/monthly', methods=['GET', 'POST'])
@login_required
def monthly():
    """Monthly wellness assessment"""
    current_month = PeriodicAssessment.get_current_month_key()

    # Check if already completed this month
    existing = PeriodicAssessment.query.filter_by(
        user_id=current_user.id,
        assessment_type='monthly',
        period_key=current_month
    ).first()

    if request.method == 'POST':
        responses = {}
        total_score = 0

        for q in MONTHLY_QUESTIONS:
            value = request.form.get(q['id'], 3)
            responses[q['id']] = int(value)
            total_score += int(value)

        avg_score = (total_score / len(MONTHLY_QUESTIONS)) * 20

        # Get previous month's assessment
        prev_month = (datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        prev_assessment = PeriodicAssessment.query.filter_by(
            user_id=current_user.id,
            assessment_type='monthly',
            period_key=prev_month
        ).first()

        improvement = 0
        if prev_assessment and prev_assessment.overall_wellness:
            improvement = avg_score - prev_assessment.overall_wellness

        if existing:
            assessment = existing
        else:
            assessment = PeriodicAssessment(
                user_id=current_user.id,
                assessment_type='monthly',
                period_key=current_month
            )

        assessment.overall_wellness = avg_score
        assessment.mental_wellness_score = responses.get('M1', 3) * 20
        assessment.sleep_quality_score = responses.get('M2', 3) * 20
        assessment.stress_level_score = responses.get('M3', 3) * 20
        assessment.digital_wellness_score = responses.get('M6', 3) * 20
        assessment.improvement_score = improvement
        assessment.set_responses(responses)
        assessment.completed_at = datetime.utcnow()

        # Generate insights
        insights = generate_monthly_insights(responses, improvement)
        assessment.set_insights(insights)

        # Snapshot current Big Five if available
        if current_user.big_five_normalized:
            assessment.set_big_five(json.loads(current_user.big_five_normalized))

        db.session.add(assessment)
        db.session.commit()

        flash('Monthly assessment completed! View your progress trends.', 'success')
        return redirect(url_for('assessment.history'))

    return render_template('assessment/monthly.html',
                         questions=MONTHLY_QUESTIONS,
                         existing=existing)


@bp.route('/history')
@login_required
def history():
    """View assessment history and progress"""
    weekly_assessments = PeriodicAssessment.query.filter_by(
        user_id=current_user.id,
        assessment_type='weekly'
    ).order_by(PeriodicAssessment.created_at.desc()).limit(12).all()

    monthly_assessments = PeriodicAssessment.query.filter_by(
        user_id=current_user.id,
        assessment_type='monthly'
    ).order_by(PeriodicAssessment.created_at.desc()).limit(12).all()

    # Calculate trends
    weekly_trend = calculate_trend([a.overall_wellness for a in weekly_assessments[:4]])
    monthly_trend = calculate_trend([a.overall_wellness for a in monthly_assessments[:3]])

    # Check if assessments are due
    current_week = PeriodicAssessment.get_current_week_key()
    current_month = PeriodicAssessment.get_current_month_key()

    weekly_due = not any(a.period_key == current_week for a in weekly_assessments)
    monthly_due = not any(a.period_key == current_month for a in monthly_assessments)

    return render_template('assessment/history.html',
                         weekly_assessments=weekly_assessments,
                         monthly_assessments=monthly_assessments,
                         weekly_trend=weekly_trend,
                         monthly_trend=monthly_trend,
                         weekly_due=weekly_due,
                         monthly_due=monthly_due)


@bp.route('/api/progress')
@login_required
def api_progress():
    """API endpoint for progress chart data"""
    weekly = PeriodicAssessment.query.filter_by(
        user_id=current_user.id,
        assessment_type='weekly'
    ).order_by(PeriodicAssessment.created_at.asc()).limit(12).all()

    monthly = PeriodicAssessment.query.filter_by(
        user_id=current_user.id,
        assessment_type='monthly'
    ).order_by(PeriodicAssessment.created_at.asc()).limit(6).all()

    return jsonify({
        'weekly': [a.to_dict() for a in weekly],
        'monthly': [a.to_dict() for a in monthly]
    })


def generate_weekly_insights(responses, improvement):
    """Generate AI-like insights from weekly responses"""
    insights = []

    mood = responses.get('W1', 3)
    sleep = responses.get('W2', 3)
    stress = responses.get('W3', 3)
    productivity = responses.get('W4', 3)
    energy = responses.get('W5', 3)
    digital = responses.get('W6', 3)

    if improvement > 10:
        insights.append("Great improvement from last week! Keep up the positive momentum.")
    elif improvement < -10:
        insights.append("This week was challenging. Remember, setbacks are part of the journey.")

    if mood >= 4 and energy >= 4:
        insights.append("Your mood and energy levels are excellent - you're thriving!")
    elif mood <= 2:
        insights.append("Low mood detected. Consider activities that bring you joy.")

    if sleep <= 2:
        insights.append("Sleep quality needs attention. Try a consistent bedtime routine.")

    if stress >= 4:
        insights.append("High stress levels. Practice deep breathing or take short breaks.")

    if digital <= 2:
        insights.append("Great job managing screen time this week!")
    elif digital >= 4:
        insights.append("Consider setting app timers to reduce screen time.")

    if not insights:
        insights.append("Balanced week overall. Maintain your healthy routines.")

    return insights


def generate_monthly_insights(responses, improvement):
    """Generate insights from monthly assessment"""
    insights = []

    mental = responses.get('M1', 3)
    balance = responses.get('M4', 3)
    goals = responses.get('M5', 3)
    selfcare = responses.get('M7', 3)
    outlook = responses.get('M8', 3)

    if improvement > 5:
        insights.append("Monthly improvement trend is positive - your efforts are paying off!")
    elif improvement < -5:
        insights.append("This month had challenges. Next month is a fresh start.")

    if mental >= 4:
        insights.append("Strong mental wellness this month - excellent self-care!")

    if balance <= 2:
        insights.append("Work-life balance needs attention. Set boundaries for personal time.")

    if goals >= 4:
        insights.append("Great progress on goals! Consider setting new milestones.")
    elif goals <= 2:
        insights.append("Break down goals into smaller, achievable steps.")

    if selfcare <= 2:
        insights.append("Prioritize self-care activities - even 10 minutes daily helps.")

    if outlook >= 4:
        insights.append("Positive outlook for the future - optimism supports wellbeing!")

    if not insights:
        insights.append("Steady month with room for growth in various areas.")

    return insights


def calculate_trend(scores):
    """Calculate trend direction from scores list"""
    scores = [s for s in scores if s is not None]
    if len(scores) < 2:
        return 'stable'

    recent = scores[:len(scores)//2]
    older = scores[len(scores)//2:]

    recent_avg = sum(recent) / len(recent) if recent else 0
    older_avg = sum(older) / len(older) if older else 0

    diff = recent_avg - older_avg
    if diff > 5:
        return 'improving'
    elif diff < -5:
        return 'declining'
    return 'stable'
