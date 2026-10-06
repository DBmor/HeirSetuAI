"""Expand company_profiles table for multi-step registration

Revision ID: add_company_registration_fields
Revises: 8c222a7265f5
Create Date: 2026-09-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_company_registration_fields'
down_revision = '8c222a7265f5'
branch_labels = None
depends_on = None


def upgrade():
    # Add representative info columns
    op.add_column('company_profiles', sa.Column('representative_name', sa.String(150), nullable=True))
    op.add_column('company_profiles', sa.Column('designation', sa.String(100), nullable=True))
    op.add_column('company_profiles', sa.Column('official_email', sa.String(150), nullable=True))
    op.add_column('company_profiles', sa.Column('email_otp_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('company_profiles', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('company_profiles', sa.Column('phone_otp_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('company_profiles', sa.Column('linkedin_profile', sa.String(255), nullable=True))
    op.add_column('company_profiles', sa.Column('government_id_path', sa.String(255), nullable=True))
    op.add_column('company_profiles', sa.Column('authorization_letter_path', sa.String(255), nullable=True))

    # Add company details columns
    op.add_column('company_profiles', sa.Column('company_legal_name', sa.String(255), nullable=True))
    op.add_column('company_profiles', sa.Column('corporate_id', sa.String(50), nullable=True))
    op.add_column('company_profiles', sa.Column('business_type', sa.String(50), nullable=True))
    op.add_column('company_profiles', sa.Column('incorporation_date', sa.Date(), nullable=True))
    op.add_column('company_profiles', sa.Column('company_email', sa.String(150), nullable=True))
    op.add_column('company_profiles', sa.Column('company_phone', sa.String(20), nullable=True))
    op.add_column('company_profiles', sa.Column('registered_address', sa.Text(), nullable=True))

    # Add documents columns
    op.add_column('company_profiles', sa.Column('incorporation_document_path', sa.String(255), nullable=True))
    op.add_column('company_profiles', sa.Column('tax_document_path', sa.String(255), nullable=True))
    op.add_column('company_profiles', sa.Column('license_document_path', sa.String(255), nullable=True))

    # Add consent columns
    op.add_column('company_profiles', sa.Column('terms_accepted', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('company_profiles', sa.Column('privacy_accepted', sa.Boolean(), nullable=False, server_default='0'))

    # Add verification status columns
    op.add_column('company_profiles', sa.Column('application_id', sa.String(50), nullable=True))
    op.add_column('company_profiles', sa.Column('registration_step', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('company_profiles', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.add_column('company_profiles', sa.Column('submitted_at', sa.DateTime(), nullable=True))
    op.add_column('company_profiles', sa.Column('verified_at', sa.DateTime(), nullable=True))
    op.add_column('company_profiles', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('company_profiles', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()))

    # Add unique constraint to application_id
    op.create_unique_constraint('uq_application_id', 'company_profiles', ['application_id'])
    
    # Rename status column to keep the old one and add new status
    # Note: if status column doesn't exist yet from previous migration, we need to create it differently
    # The existing migration likely has it as default 'pending', so we update it here
    op.alter_column('company_profiles', 'status', new_column_name='verification_status', existing_type=sa.String(20))


def downgrade():
    # Remove unique constraint
    op.drop_constraint('uq_application_id', 'company_profiles')
    
    # Rename status column back
    op.alter_column('company_profiles', 'verification_status', new_column_name='status', existing_type=sa.String(20))
    
    # Remove columns in reverse order
    op.drop_column('company_profiles', 'updated_at')
    op.drop_column('company_profiles', 'created_at')
    op.drop_column('company_profiles', 'verified_at')
    op.drop_column('company_profiles', 'submitted_at')
    op.drop_column('company_profiles', 'rejection_reason')
    op.drop_column('company_profiles', 'registration_step')
    op.drop_column('company_profiles', 'application_id')
    op.drop_column('company_profiles', 'privacy_accepted')
    op.drop_column('company_profiles', 'terms_accepted')
    op.drop_column('company_profiles', 'license_document_path')
    op.drop_column('company_profiles', 'tax_document_path')
    op.drop_column('company_profiles', 'incorporation_document_path')
    op.drop_column('company_profiles', 'registered_address')
    op.drop_column('company_profiles', 'company_phone')
    op.drop_column('company_profiles', 'company_email')
    op.drop_column('company_profiles', 'incorporation_date')
    op.drop_column('company_profiles', 'business_type')
    op.drop_column('company_profiles', 'corporate_id')
    op.drop_column('company_profiles', 'company_legal_name')
    op.drop_column('company_profiles', 'authorization_letter_path')
    op.drop_column('company_profiles', 'government_id_path')
    op.drop_column('company_profiles', 'linkedin_profile')
    op.drop_column('company_profiles', 'phone_otp_verified')
    op.drop_column('company_profiles', 'phone')
    op.drop_column('company_profiles', 'email_otp_verified')
    op.drop_column('company_profiles', 'official_email')
    op.drop_column('company_profiles', 'designation')
    op.drop_column('company_profiles', 'representative_name')
