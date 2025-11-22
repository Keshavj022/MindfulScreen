from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app import db, csrf
from app.models import QuizResponse
from app.services.quiz_service import QuizService
from app.services.knowledge_graph import KnowledgeGraphService
from datetime import datetime

bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@bp.route('/start')
@login_required
def start():
    if current_user.quiz_completed:
        return redirect(url_for('main.index'))
    return render_template('quiz/quiz.html')

@bp.route('/api/questions')
@login_required
def get_questions():
    quiz_service = QuizService()
    return jsonify(quiz_service.get_all_questions())

@bp.route('/api/submit', methods=['POST'])
@csrf.exempt
@login_required
def submit_quiz():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        responses = data.get('responses', {})
        if not responses:
            return jsonify({'success': False, 'error': 'No responses provided'}), 400

        # Save individual responses
        for question_id, answer in responses.items():
            try:
                quiz_response = QuizResponse(
                    user_id=current_user.id,
                    question_id=question_id,
                    answer=int(answer)
                )
                db.session.add(quiz_response)
            except (ValueError, TypeError) as e:
                print(f"Error saving response {question_id}: {e}")
                continue

        # Analyze responses using ML-based classification
        quiz_service = QuizService()
        results = quiz_service.analyze_responses(responses)

        # Update user profile with comprehensive results
        current_user.quiz_completed = True
        current_user.personality_type = results['personality_type']
        current_user.personality_description = results.get('personality_description', '')
        current_user.big_five_scores = results['big_five_scores']
        current_user.big_five_normalized = results.get('big_five_normalized', {})
        current_user.personality_cluster = results.get('cluster')
        current_user.cluster_confidence = results.get('cluster_confidence')
        current_user.strengths = results.get('strengths', [])
        current_user.growth_areas = results.get('growth_areas', [])
        current_user.stress_level = results['stress_level']
        current_user.wellness_goals = results['wellness_goals']

        # Mental health tracking
        mental_health = results.get('mental_health', {})
        current_user.mental_wellness_index = mental_health.get('wellness_index')
        current_user.mental_health_status = mental_health.get('status')
        current_user.mental_health_scores = mental_health.get('category_scores', {})
        current_user.mental_health_recommendations = mental_health.get('recommendations', [])

        # Digital wellness tracking
        digital_wellness = results.get('digital_wellness', {})
        current_user.digital_wellness_index = digital_wellness.get('wellness_index')
        current_user.digital_wellness_risk = digital_wellness.get('risk_level')
        current_user.digital_wellness_scores = digital_wellness.get('category_scores', {})

        # Initialize wellness history for progress tracking
        current_user.last_assessment_date = datetime.utcnow()
        if not current_user.wellness_history:
            current_user.wellness_history = []

        # Add current assessment to history
        history_entry = {
            'date': datetime.utcnow().isoformat(),
            'mental_wellness_index': mental_health.get('wellness_index'),
            'digital_wellness_index': digital_wellness.get('wellness_index'),
            'stress_level': results['stress_level']
        }
        history = list(current_user.wellness_history) if current_user.wellness_history else []
        history.append(history_entry)
        current_user.wellness_history = history

        db.session.commit()

        # Create knowledge graph
        try:
            kg_service = KnowledgeGraphService()
            kg_service.create_or_update_graph(current_user.id)
        except Exception as kg_error:
            print(f"Knowledge graph error: {kg_error}")

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        db.session.rollback()
        print(f"Quiz submit error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/results')
@login_required
def results():
    if not current_user.quiz_completed:
        return redirect(url_for('quiz.start'))
    return render_template('quiz/results.html')

@bp.route('/api/retake', methods=['POST'])
@csrf.exempt
@login_required
def retake_quiz():
    """Allow user to retake the quiz for updated assessment"""
    try:
        # Clear previous responses
        QuizResponse.query.filter_by(user_id=current_user.id).delete()

        # Reset quiz status but keep history
        current_user.quiz_completed = False

        db.session.commit()

        return jsonify({'success': True, 'message': 'You can now retake the quiz'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/progress')
@login_required
def get_progress():
    """Get user's wellness progress over time"""
    history = current_user.wellness_history or []

    return jsonify({
        'history': history,
        'current': {
            'mental_wellness_index': current_user.mental_wellness_index,
            'digital_wellness_index': current_user.digital_wellness_index,
            'stress_level': current_user.stress_level,
            'personality_type': current_user.personality_type
        },
        'last_assessment': current_user.last_assessment_date.isoformat() if current_user.last_assessment_date else None
    })
