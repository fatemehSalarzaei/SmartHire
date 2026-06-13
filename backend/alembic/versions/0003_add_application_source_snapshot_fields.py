"""add application source snapshot fields

Revision ID: 0003_add_application_source_snapshot_fields
Revises: 0002_add_user_password_hash
Create Date: 2026-06-13 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0003_add_application_source_snapshot_fields"
down_revision: str | None = "0002_add_user_password_hash"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("kando_application_sources", sa.Column("kando_cv_id", sa.Integer(), nullable=True))
    op.add_column("kando_application_sources", sa.Column("cover_letter", sa.Text(), nullable=True))
    op.add_column(
        "kando_application_sources",
        sa.Column("total_work_experience_months", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_kando_application_sources_kando_cv_id",
        "kando_application_sources",
        ["kando_cv_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_kando_application_sources_kando_cv_id", table_name="kando_application_sources")
    op.drop_column("kando_application_sources", "total_work_experience_months")
    op.drop_column("kando_application_sources", "cover_letter")
    op.drop_column("kando_application_sources", "kando_cv_id")
