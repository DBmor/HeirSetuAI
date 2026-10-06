# app/blueprints/auth/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, DateField, TextAreaField, BooleanField, TelField, URLField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, Regexp
import re


class CompanyRegistrationStep1Form(FlaskForm):
    """Representative verification - Step 1"""
    representative_name = StringField(
        'Full name',
        validators=[DataRequired(message="Name is required"), Length(min=2, max=150)]
    )
    designation = StringField(
        'Designation',
        validators=[DataRequired(message="Designation is required"), Length(min=2, max=100)]
    )
    official_email = StringField(
        'Official company email',
        validators=[DataRequired(), Email()]
    )
    phone = TelField(
        'Phone number',
        validators=[DataRequired(), Regexp(r'^\+?[\d\s\-()]{7,}$', message="Invalid phone format")]
    )
    linkedin = URLField(
        'LinkedIn profile',
        validators=[Optional()]
    )
    government_id = FileField(
        'Government ID',
        validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF or image files only')]
    )
    authorization_letter = FileField(
        'Authorization letter',
        validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF or image files only')]
    )
    representative_consent = BooleanField(
        'I am an authorized representative',
        validators=[DataRequired()]
    )
    accuracy_consent = BooleanField(
        'Information is true and accurate',
        validators=[DataRequired()]
    )


class CompanyRegistrationStep2Form(FlaskForm):
    """Company details - Step 2"""
    company_name = StringField(
        'Company legal name',
        validators=[DataRequired(), Length(min=2, max=255)]
    )
    corporate_id = StringField(
        'CIN / GST / PAN number',
        validators=[DataRequired(), Length(min=5, max=50)]
    )
    business_type = SelectField(
        'Business type',
        choices=[
            ('', 'Select business type'),
            ('Private Limited', 'Private Limited'),
            ('Public Limited', 'Public Limited'),
            ('Partnership', 'Partnership'),
            ('LLP', 'LLP'),
            ('Sole Proprietorship', 'Sole Proprietorship'),
        ],
        validators=[DataRequired()]
    )
    incorporation_date = DateField(
        'Date of incorporation',
        validators=[Optional()]
    )
    company_email = StringField(
        'Official company email',
        validators=[Optional(), Email()]
    )
    company_phone = TelField(
        'Company phone number',
        validators=[Optional(), Regexp(r'^\+?[\d\s\-()]{7,}$', message="Invalid phone format")]
    )
    website = URLField(
        'Company website',
        validators=[DataRequired()]
    )
    registered_address = TextAreaField(
        'Registered address',
        validators=[DataRequired(), Length(min=10, max=500)]
    )


class CompanyRegistrationStep3Form(FlaskForm):
    """Document upload - Step 3"""
    incorporation_document = FileField(
        'Certificate of incorporation',
        validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF or image files only')]
    )
    tax_document = FileField(
        'GST / PAN document',
        validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF or image files only')]
    )
    license_document = FileField(
        'Business license / owner ID',
        validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF or image files only')]
    )


class CompanyRegistrationStep4Form(FlaskForm):
    """Security & consent - Step 4"""
    password = PasswordField(
        'Create password',
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters")]
    )
    confirm_password = PasswordField(
        'Confirm password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    verification_consent = BooleanField(
        'Information provided is true',
        validators=[DataRequired()]
    )
    terms_consent = BooleanField(
        'I agree to Terms & Conditions and Privacy Policy',
        validators=[DataRequired()]
    )


class CandidateRegistrationForm(FlaskForm):
    """Candidate registration (simplified)"""
    name = StringField(
        'Full name',
        validators=[DataRequired(), Length(min=2, max=150)]
    )
    email = StringField(
        'Email address',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters")]
    )
    confirm_password = PasswordField(
        'Confirm password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    terms_consent = BooleanField(
        'I agree to Terms & Conditions',
        validators=[DataRequired()]
    )
