from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.services.email_service import get_email_service
import re
from datetime import datetime

bp = Blueprint('auth', __name__)

# Email validation regex
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


def validate_password(password):
    """Validate password strength"""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    if not re.search(r'[@$!%*?&#]', password):
        errors.append("Password must contain at least one special character (@$!%*?&#)")
    return errors


def validate_email(email):
    """Validate email format"""
    if not EMAIL_PATTERN.match(email):
        return False
    return True


def get_password_strength(password):
    """Calculate password strength score"""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[@$!%*?&#]', password):
        score += 1

    if score <= 2:
        return 'weak'
    elif score <= 4:
        return 'medium'
    else:
        return 'strong'


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        if not email or not password:
            flash('Please enter both email and password', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Check if email is verified (if the field exists)
            if hasattr(user, 'email_verified') and user.email_verified == False:
                session['pending_verification_email'] = email
                flash('Please verify your email before logging in', 'warning')
                return redirect(url_for('auth.resend_verification'))

            login_user(user, remember=remember)
            user.update_last_login()

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('auth/login.html')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        country_code = request.form.get('country_code', '')
        phone = request.form.get('phone', '').strip()
        age = request.form.get('age')
        gender = request.form.get('gender')
        occupation = request.form.get('occupation', '').strip()
        country = request.form.get('country', '')
        city = request.form.get('city', '').strip()

        # Consent checkboxes
        terms_accepted = request.form.get('terms_accepted') == 'on'
        privacy_accepted = request.form.get('privacy_accepted') == 'on'
        marketing_consent = request.form.get('marketing_consent') == 'on'

        # Validation
        errors = []

        if not name or len(name) < 2:
            errors.append("Please enter a valid name (at least 2 characters)")

        if not validate_email(email):
            errors.append("Please enter a valid email address")

        if User.query.filter_by(email=email).first():
            errors.append("This email is already registered")

        password_errors = validate_password(password)
        if password_errors:
            errors.extend(password_errors)

        if password != confirm_password:
            errors.append("Passwords do not match")

        if not terms_accepted:
            errors.append("You must accept the Terms and Conditions")

        if not privacy_accepted:
            errors.append("You must accept the Privacy Policy")

        if age:
            try:
                age_int = int(age)
                if age_int < 18 or age_int > 120:
                    errors.append("You must be at least 18 years old to use MindfulScreen")
            except ValueError:
                errors.append("Please enter a valid age")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/signup.html')

        # Format phone with country code
        full_phone = f"{country_code}{phone}" if phone and country_code else phone

        # Format location
        location = f"{city}, {country}" if city and country else country or city

        # Store registration data in session for OTP verification
        session['registration_data'] = {
            'name': name,
            'email': email,
            'password': password,
            'phone': full_phone,
            'age': int(age) if age else None,
            'gender': gender,
            'occupation': occupation,
            'location': location,
            'country': country,
            'city': city,
            'terms_accepted': terms_accepted,
            'privacy_accepted': privacy_accepted,
            'marketing_consent': marketing_consent
        }

        user = User(
            name=name,
            email=email,
            phone=full_phone,
            age=int(age) if age else None,
            gender=gender,
            occupation=occupation,
            location=location,
            email_verified=True,  # Skip verification for now
            terms_accepted_at=datetime.utcnow(),
            privacy_accepted_at=datetime.utcnow(),
            marketing_consent=marketing_consent
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Log in user
        login_user(user)
        flash('Account created successfully! Welcome to MindfulScreen.', 'success')
        return redirect(url_for('quiz.start'))

    return render_template('auth/signup.html')


@bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if 'registration_data' not in session:
        flash('Please complete the registration form first', 'warning')
        return redirect(url_for('auth.signup'))

    reg_data = session['registration_data']

    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()

        email_service = get_email_service()
        success, message = email_service.verify_otp(reg_data['email'], otp)

        if success:
            # Create user account
            user = User(
                name=reg_data['name'],
                email=reg_data['email'],
                phone=reg_data['phone'],
                age=reg_data['age'],
                gender=reg_data['gender'],
                occupation=reg_data['occupation'],
                location=reg_data['location'],
                email_verified=True,
                terms_accepted_at=datetime.utcnow(),
                privacy_accepted_at=datetime.utcnow(),
                marketing_consent=reg_data['marketing_consent']
            )
            user.set_password(reg_data['password'])

            db.session.add(user)
            db.session.commit()

            # Clear session
            del session['registration_data']

            # Send welcome email
            email_service.send_welcome_email(reg_data['email'], reg_data['name'])

            # Log in user
            login_user(user)
            flash('Account created successfully! Please complete the personality quiz.', 'success')
            return redirect(url_for('quiz.start'))
        else:
            flash(message, 'danger')

    return render_template('auth/verify_email.html', email=reg_data['email'])


@bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    if 'registration_data' not in session:
        return jsonify({'success': False, 'error': 'Session expired'}), 400

    reg_data = session['registration_data']
    email_service = get_email_service()

    if email_service.send_otp_email(reg_data['email'], reg_data['name']):
        return jsonify({'success': True, 'message': 'OTP sent successfully'})
    else:
        return jsonify({'success': False, 'error': 'Failed to send OTP'}), 500


@bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    email = session.get('pending_verification_email')
    if not email:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        user = User.query.filter_by(email=email).first()
        if user:
            email_service = get_email_service()
            email_service.send_otp_email(email, user.name)
            flash('Verification email sent', 'success')

    return render_template('auth/resend_verification.html', email=email)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        # Always show same message for security
        flash('If an account exists with this email, you will receive password reset instructions.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@bp.route('/api/validate-email', methods=['POST'])
def api_validate_email():
    """API endpoint to check email availability"""
    data = request.get_json(force=True, silent=True) or {}
    email = data.get('email', '').strip().lower()

    if not validate_email(email):
        return jsonify({'valid': False, 'error': 'Invalid email format'})

    if User.query.filter_by(email=email).first():
        return jsonify({'valid': False, 'error': 'Email already registered'})

    return jsonify({'valid': True})


@bp.route('/api/validate-password', methods=['POST'])
def api_validate_password():
    """API endpoint to validate password strength"""
    data = request.get_json(force=True, silent=True) or {}
    password = data.get('password', '')
    errors = validate_password(password)

    return jsonify({
        'valid': len(errors) == 0,
        'errors': errors,
        'strength': get_password_strength(password)
    })
