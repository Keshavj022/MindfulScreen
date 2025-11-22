"""
Email Service for MindfulScreen
Handles all email communications including OTP verification, welcome emails, etc.
"""

import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import current_app, render_template_string
import os

# In-memory OTP storage (use Redis in production)
otp_storage = {}


class EmailService:
    def __init__(self):
        # Use Flask config or environment variables
        self.smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('MAIL_PORT', 587))
        self.use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        self.use_ssl = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
        self.smtp_username = os.getenv('MAIL_USERNAME', '')
        self.smtp_password = os.getenv('MAIL_PASSWORD', '')

        # Parse MAIL_DEFAULT_SENDER which might be "Name <email>" format
        default_sender = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@mindfulscreen.com')
        if '<' in default_sender and '>' in default_sender:
            # Extract email from "Name <email>" format
            import re
            match = re.search(r'<(.+)>', default_sender)
            self.from_email = match.group(1) if match else default_sender
            self.from_name = default_sender.split('<')[0].strip()
        else:
            self.from_email = default_sender
            self.from_name = 'MindfulScreen'

        # OTP settings
        self.otp_expiry_minutes = int(os.getenv('OTP_EXPIRY_MINUTES', 10))
        self.otp_max_attempts = int(os.getenv('OTP_MAX_ATTEMPTS', 3))

    def _get_smtp_connection(self):
        """Create SMTP connection"""
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()

            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            return server
        except Exception as e:
            print(f"SMTP Connection Error: {e}")
            return None

    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send an email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Plain text version
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            # HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            server = self._get_smtp_connection()
            if server:
                server.sendmail(self.from_email, to_email, msg.as_string())
                server.quit()
                return True
            else:
                # Log email for development (when SMTP not configured)
                print(f"[EMAIL] To: {to_email}, Subject: {subject}")
                print(f"[EMAIL] Content preview: {html_content[:200]}...")
                return True  # Return True for dev mode
        except Exception as e:
            print(f"Email send error: {e}")
            return False

    def generate_otp(self, email, length=6):
        """Generate and store OTP for email verification"""
        otp = ''.join(random.choices(string.digits, k=length))
        expiry = datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)

        otp_storage[email] = {
            'otp': otp,
            'expiry': expiry,
            'attempts': 0
        }

        return otp

    def verify_otp(self, email, otp):
        """Verify OTP for email"""
        if email not in otp_storage:
            return False, "OTP expired or not found. Please request a new one."

        stored = otp_storage[email]

        # Check expiry
        if datetime.utcnow() > stored['expiry']:
            del otp_storage[email]
            return False, "OTP has expired. Please request a new one."

        # Check attempts
        if stored['attempts'] >= self.otp_max_attempts:
            del otp_storage[email]
            return False, "Too many failed attempts. Please request a new OTP."

        # Verify OTP
        if stored['otp'] == otp:
            del otp_storage[email]
            return True, "Email verified successfully!"

        stored['attempts'] += 1
        remaining = self.otp_max_attempts - stored['attempts']
        return False, f"Invalid OTP. {remaining} attempt{'s' if remaining != 1 else ''} remaining."

    def send_otp_email(self, to_email, name):
        """Send OTP verification email"""
        otp = self.generate_otp(to_email)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-box {{ background: white; padding: 20px; text-align: center; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .otp-code {{ font-size: 36px; font-weight: bold; color: #6366f1; letter-spacing: 8px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .warning {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 15px; font-size: 13px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MindfulScreen</h1>
                    <p>Email Verification</p>
                </div>
                <div class="content">
                    <p>Hello <strong>{name}</strong>,</p>
                    <p>Thank you for signing up for MindfulScreen! Please use the following OTP to verify your email address:</p>

                    <div class="otp-box">
                        <p style="margin: 0; color: #666;">Your verification code is:</p>
                        <p class="otp-code">{otp}</p>
                        <p style="margin: 0; color: #999; font-size: 13px;">Valid for 10 minutes</p>
                    </div>

                    <p>If you didn't create an account with MindfulScreen, please ignore this email.</p>

                    <div class="warning">
                        <strong>Security Tip:</strong> Never share this OTP with anyone. MindfulScreen will never ask for your OTP via phone or email.
                    </div>
                </div>
                <div class="footer">
                    <p>&copy; 2025 MindfulScreen. All rights reserved.</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Hello {name},

        Thank you for signing up for MindfulScreen!

        Your verification code is: {otp}

        This code is valid for 10 minutes.

        If you didn't create an account, please ignore this email.

        - MindfulScreen Team
        """

        return self.send_email(to_email, "Verify Your Email - MindfulScreen", html_content, text_content)

    def send_welcome_email(self, to_email, name):
        """Send welcome email after successful registration"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 40px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .feature {{ margin: 15px 0; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #6366f1; }}
                .feature-title {{ display: flex; align-items: center; margin-bottom: 8px; }}
                .feature-icon {{ width: 32px; height: 32px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 12px; color: white; font-size: 14px; font-weight: bold; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: 600; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0 0 10px 0;">Welcome to MindfulScreen!</h1>
                    <p style="margin: 0; opacity: 0.9;">Your journey to digital wellness starts now</p>
                </div>
                <div class="content">
                    <p>Hello <strong>{name}</strong>,</p>
                    <p>We're thrilled to have you join the MindfulScreen community! You've taken the first step towards understanding and improving your digital wellbeing.</p>

                    <h3 style="color: #6366f1; margin-top: 25px;">What you can do with MindfulScreen:</h3>

                    <div class="feature">
                        <div class="feature-title">
                            <span class="feature-icon">1</span>
                            <strong style="font-size: 16px;">Personality Assessment</strong>
                        </div>
                        <p style="margin: 0; color: #666; font-size: 14px; padding-left: 44px;">Discover your personality type with our ML-powered Big Five assessment</p>
                    </div>

                    <div class="feature">
                        <div class="feature-title">
                            <span class="feature-icon">2</span>
                            <strong style="font-size: 16px;">Screen Time Analysis</strong>
                        </div>
                        <p style="margin: 0; color: #666; font-size: 14px; padding-left: 44px;">Get AI-powered insights on your digital habits and content consumption</p>
                    </div>

                    <div class="feature">
                        <div class="feature-title">
                            <span class="feature-icon">3</span>
                            <strong style="font-size: 16px;">Personalized Recommendations</strong>
                        </div>
                        <p style="margin: 0; color: #666; font-size: 14px; padding-left: 44px;">Receive tailored tips to improve your mental and digital wellness</p>
                    </div>

                    <div class="feature">
                        <div class="feature-title">
                            <span class="feature-icon">4</span>
                            <strong style="font-size: 16px;">Progress Tracking</strong>
                        </div>
                        <p style="margin: 0; color: #666; font-size: 14px; padding-left: 44px;">Monitor your improvement over time with detailed analytics</p>
                    </div>

                    <div style="text-align: center; margin-top: 30px;">
                        <a href="#" class="cta-button" style="color: white;">Start Your Assessment</a>
                    </div>

                    <p style="margin-top: 25px;">If you have any questions, feel free to reach out to our support team.</p>

                    <p>Here's to a healthier digital life!</p>
                    <p><strong>The MindfulScreen Team</strong></p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 MindfulScreen. All rights reserved.</p>
                    <p>You're receiving this email because you signed up for MindfulScreen.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to MindfulScreen, {name}!

        We're thrilled to have you join our community. You've taken the first step towards understanding and improving your digital wellbeing.

        What you can do with MindfulScreen:
        - Personality Assessment: Discover your personality type
        - Screen Time Analysis: Get AI-powered insights
        - Personalized Recommendations: Receive tailored wellness tips
        - Progress Tracking: Monitor your improvement

        Here's to a healthier digital life!
        The MindfulScreen Team
        """

        return self.send_email(to_email, "Welcome to MindfulScreen! 🎉", html_content, text_content)

    def send_password_reset_email(self, to_email, name, reset_token):
        """Send password reset email"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .cta-button {{ display: inline-block; background: #6366f1; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .warning {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 15px; font-size: 13px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MindfulScreen</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <p>Hello <strong>{name}</strong>,</p>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>

                    <div style="text-align: center;">
                        <a href="#reset-link/{reset_token}" class="cta-button">Reset Password</a>
                    </div>

                    <p>This link will expire in 1 hour for security reasons.</p>

                    <div class="warning">
                        <strong>Didn't request this?</strong> If you didn't request a password reset, please ignore this email or contact support if you're concerned about your account security.
                    </div>
                </div>
                <div class="footer">
                    <p>&copy; 2025 MindfulScreen. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, "Reset Your Password - MindfulScreen", html_content)


# Global instance
_email_service = None

def get_email_service():
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
