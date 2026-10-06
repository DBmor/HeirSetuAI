# app/utils/email_utils.py
from flask import render_template_string
from flask_mail import Mail, Message
import os


def send_otp_email(recipient_email, otp, template_type="registration"):
    """
    Send OTP via email
    
    Args:
        recipient_email: Email address to send to
        otp: One-time password (6 digits)
        template_type: Type of email (registration, password_reset, etc.)
    """
    try:
        # Import Mail from extensions (circular import prevention)
        from app.extensions import mail
        
        subject = "Your verification code - HeirSetuAI"
        
        # Email templates
        templates = {
            "registration": f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #333; margin-bottom: 20px;">Verify Your Email</h2>
                        <p style="color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                            Your verification code for HeirSetuAI registration is:
                        </p>
                        <div style="background-color: #f0f0f0; border-left: 4px solid #0066cc; padding: 20px; margin: 30px 0; text-align: center;">
                            <h1 style="color: #0066cc; letter-spacing: 2px; margin: 0; font-size: 32px; font-weight: bold;">{otp}</h1>
                        </div>
                        <p style="color: #666; font-size: 14px; line-height: 1.6;">
                            This code will expire in 10 minutes. If you didn't request this code, please ignore this email.
                        </p>
                        <p style="color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                            HeirSetuAI - Trusted Hiring Platform<br>
                            🔒 Your security is our priority
                        </p>
                    </div>
                </body>
            </html>
            """,
            
            "password_reset": f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #333; margin-bottom: 20px;">Reset Your Password</h2>
                        <p style="color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                            Use this code to reset your password:
                        </p>
                        <div style="background-color: #f0f0f0; border-left: 4px solid #0066cc; padding: 20px; margin: 30px 0; text-align: center;">
                            <h1 style="color: #0066cc; letter-spacing: 2px; margin: 0; font-size: 32px; font-weight: bold;">{otp}</h1>
                        </div>
                        <p style="color: #666; font-size: 14px; line-height: 1.6;">
                            This code will expire in 15 minutes.
                        </p>
                    </div>
                </body>
            </html>
            """
        }
        
        html_body = templates.get(template_type, templates["registration"])
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=html_body
        )
        
        mail.send(msg)
        return True
    
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")
        # In production, log this to error tracking service
        return False


def send_verification_email(user_email, verification_link):
    """Send account verification email"""
    try:
        from app.extensions import mail
        
        subject = "Verify Your HeirSetuAI Account"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-bottom: 20px;">Welcome to HeirSetuAI</h2>
                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                        Please verify your email address to complete your registration.
                    </p>
                    <a href="{verification_link}" style="display: inline-block; background-color: #0066cc; color: white; padding: 12px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; margin: 30px 0;">
                        Verify Email Address
                    </a>
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        Or copy this link in your browser:<br>
                        <span style="word-break: break-all; color: #0066cc;">{verification_link}</span>
                    </p>
                    <p style="color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                        This link will expire in 24 hours.
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body
        )
        
        mail.send(msg)
        return True
    
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return False


def send_company_approval_email(company_email, company_name, status):
    """Send company registration status email"""
    try:
        from app.extensions import mail
        
        if status == "approved":
            subject = "Congratulations! Your Company is Verified - HeirSetuAI"
            message_text = """
            <p style="color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                Great news! Your company has been verified and approved on HeirSetuAI.
            </p>
            <p style="color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                You can now:
            </p>
            <ul style="color: #666; font-size: 14px; line-height: 1.8;">
                <li>Post job listings</li>
                <li>Review candidate applications</li>
                <li>Access background check reports</li>
                <li>Manage your company profile</li>
            </ul>
            """
        else:
            subject = "Update on Your Company Registration - HeirSetuAI"
            message_text = """
            <p style="color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                We've reviewed your registration. Please contact our support team for more information.
            </p>
            """
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-bottom: 20px;">Company Registration Update</h2>
                    <p style="color: #666; font-size: 14px; margin-bottom: 20px;">Hello {company_name},</p>
                    {message_text}
                    <p style="color: #666; font-size: 14px; line-height: 1.6; margin-top: 30px;">
                        Best regards,<br>
                        HeirSetuAI Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[company_email],
            html=html_body
        )
        
        mail.send(msg)
        return True
    
    except Exception as e:
        print(f"Error sending company email: {str(e)}")
        return False
