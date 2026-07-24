"""Create the simplified Agent Arena beta schema.

Revision ID: 0001_initial_beta
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_beta"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_name", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("active_submission_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("owner_name", "name", name="uq_owner_agent_name"),
    )
    op.create_index("ix_agents_owner_name", "agents", ["owner_name"])
    op.create_table(
        "submissions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("agent_id", sa.String(length=36), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column("source_path", sa.Text(), nullable=False),
        sa.Column("execution_kind", sa.String(length=20), nullable=False),
        sa.Column("validation_result", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("agent_id", "number", name="uq_agent_submission"),
    )
    op.create_index("ix_submissions_agent_id", "submissions", ["agent_id"])
    op.create_table(
        "fixtures",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "submission_a_id",
            sa.String(length=36),
            sa.ForeignKey("submissions.id"),
            nullable=False,
        ),
        sa.Column(
            "submission_b_id",
            sa.String(length=36),
            sa.ForeignKey("submissions.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_fixtures_submission_a_id", "fixtures", ["submission_a_id"])
    op.create_index("ix_fixtures_submission_b_id", "fixtures", ["submission_b_id"])
    op.create_index("ix_fixtures_status", "fixtures", ["status"])
    op.create_table(
        "games",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("fixture_id", sa.String(length=36), sa.ForeignKey("fixtures.id"), nullable=False),
        sa.Column("leg_number", sa.Integer(), nullable=False),
        sa.Column(
            "first_submission_id",
            sa.String(length=36),
            sa.ForeignKey("submissions.id"),
            nullable=False,
        ),
        sa.Column(
            "second_submission_id",
            sa.String(length=36),
            sa.ForeignKey("submissions.id"),
            nullable=False,
        ),
        sa.Column("winner_submission_id", sa.String(length=36), nullable=True),
        sa.Column("end_status", sa.String(length=30), nullable=False),
        sa.Column("losing_reason", sa.Text(), nullable=False),
        sa.Column("replay", sa.JSON(), nullable=False),
        sa.Column("engine_version", sa.String(length=80), nullable=False),
        sa.Column("ruleset_version", sa.String(length=80), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("fixture_id", "leg_number", name="uq_fixture_leg"),
    )
    op.create_index("ix_games_fixture_id", "games", ["fixture_id"])


def downgrade() -> None:
    op.drop_table("games")
    op.drop_table("fixtures")
    op.drop_table("submissions")
    op.drop_table("agents")
