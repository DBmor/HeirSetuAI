"""Add candidate profiles and resumes tables

Revision ID: add_candidate_tables
Revises: add_company_registration_fields
Create Date: 2026-09-01 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_candidate_tables'
down_revision = 'add_company_registration_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Create candidate_profiles table
    op.create_table('candidate_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('headline', sa.String(255), nullable=True),
        sa.Column('experience_level', sa.String(50), nullable=True),
        sa.Column('total_experience_years', sa.Float(), nullable=True),
        sa.Column('current_title', sa.String(150), nullable=True),
        sa.Column('current_company', sa.String(150), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('languages', sa.JSON(), nullable=True),
        sa.Column('education', sa.JSON(), nullable=True),
        sa.Column('linkedin_url', sa.String(255), nullable=True),
        sa.Column('github_url', sa.String(255), nullable=True),
        sa.Column('portfolio_url', sa.String(255), nullable=True),
        sa.Column('primary_resume_id', sa.Integer(), nullable=True),
        sa.Column('resume_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('job_preferences', sa.JSON(), nullable=True),
        sa.Column('preferred_job_types', sa.JSON(), nullable=True),
        sa.Column('preferred_locations', sa.JSON(), nullable=True),
        sa.Column('profile_completion', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_open_to_work', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='public'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create resumes table
    op.create_table('resumes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('parsed_data', sa.JSON(), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('experience_years', sa.Float(), nullable=True),
        sa.Column('scan_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('missing_keywords', sa.JSON(), nullable=True),
        sa.Column('scan_results', sa.JSON(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on user_id for faster queries
    op.create_index('ix_resumes_user_id', 'resumes', ['user_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_resumes_user_id', table_name='resumes')

    # Drop tables
    op.drop_table('resumes')
    op.drop_table('candidate_profiles')
