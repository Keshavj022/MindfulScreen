from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.services.knowledge_graph import KnowledgeGraphService

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('main/landing.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')

@bp.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def api_profile():
    if request.method == 'GET':
        return jsonify({
            'name': current_user.name,
            'email': current_user.email,
            'phone': current_user.phone,
            'age': current_user.age,
            'gender': current_user.gender,
            'occupation': current_user.occupation,
            'location': current_user.location,
            'quiz_completed': current_user.quiz_completed,
            'personality_type': current_user.personality_type
        })

    data = request.json
    current_user.name = data.get('name', current_user.name)
    current_user.phone = data.get('phone', current_user.phone)
    current_user.age = data.get('age', current_user.age)
    current_user.gender = data.get('gender', current_user.gender)
    current_user.occupation = data.get('occupation', current_user.occupation)
    current_user.location = data.get('location', current_user.location)

    db.session.commit()

    kg_service = KnowledgeGraphService()
    kg_service.update_user_graph(current_user.id)

    return jsonify({'success': True, 'message': 'Profile updated successfully'})

@bp.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_user.check_password(current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Password changed successfully'})

@bp.route('/api/wellness-goals', methods=['POST', 'DELETE'])
@login_required
def manage_wellness_goals():
    data = request.json
    goal = data.get('goal')

    if not goal:
        return jsonify({'success': False, 'message': 'Goal is required'}), 400

    if request.method == 'POST':
        # Add goal
        if current_user.wellness_goals is None:
            current_user.wellness_goals = []

        if goal not in current_user.wellness_goals:
            goals = list(current_user.wellness_goals)
            goals.append(goal)
            current_user.wellness_goals = goals
            db.session.commit()

            # Update knowledge graph
            kg_service = KnowledgeGraphService()
            kg_service.update_user_graph(current_user.id)

        return jsonify({'success': True, 'message': 'Goal added successfully'})

    elif request.method == 'DELETE':
        # Remove goal
        if current_user.wellness_goals and goal in current_user.wellness_goals:
            goals = [g for g in current_user.wellness_goals if g != goal]
            current_user.wellness_goals = goals
            db.session.commit()

            # Update knowledge graph
            kg_service = KnowledgeGraphService()
            kg_service.update_user_graph(current_user.id)

        return jsonify({'success': True, 'message': 'Goal removed successfully'})

@bp.route('/showcase')
def showcase():
    return render_template('main/showcase.html')
