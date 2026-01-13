from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    provider_enum = postgresql.ENUM("telegram", "vk", name="provider", create_type=True)
    provider_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.Enum("telegram", "vk", name="provider"), nullable=False),
        sa.Column("provider_user_id", sa.String(length=64), nullable=False),

        sa.Column("nickname", sa.String(length=32), nullable=True),
        sa.Column("is_blocked", sa.Boolean(), nullable=False, server_default=sa.text("false")),

        sa.Column("currency", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skins", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),

        sa.Column("dau_count", sa.Integer(), nullable=False, server_default="0"),

        sa.Column("total_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("daily_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("weekly_points", sa.Integer(), nullable=False, server_default="0"),

        sa.Column("last_daily_reset_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_weekly_reset_at", sa.DateTime(timezone=True), nullable=True),

        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("nickname", name="uq_users_nickname"),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_users_provider_uid"),
    )
    op.create_index("ix_users_total_points", "users", ["total_points"])

    op.create_table(
        "score_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_score_events_user_time", "score_events", ["user_id", "created_at"])

    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )

def downgrade():
    op.drop_table("app_settings")
    op.drop_index("ix_score_events_user_time", table_name="score_events")
    op.drop_table("score_events")
    op.drop_index("ix_users_total_points", table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS provider")
