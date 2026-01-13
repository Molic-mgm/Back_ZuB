from alembic import op
import sqlalchemy as sa

revision = "0002_add_prizes_referrals"
down_revision = "0001_init"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("referral_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("score_events", sa.Column("ip_address", sa.String(length=64), nullable=True))
    op.add_column("score_events", sa.Column("is_suspicious", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    op.create_table(
        "prizes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("place_from", sa.Integer(), nullable=False),
        sa.Column("place_to", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "user_prizes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prize_id", sa.Integer(), sa.ForeignKey("prizes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="awarded"),
        sa.Column("issued_by", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("awarded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

def downgrade():
    op.drop_table("user_prizes")
    op.drop_table("prizes")
    op.drop_column("score_events", "is_suspicious")
    op.drop_column("score_events", "ip_address")
    op.drop_column("users", "referral_count")
