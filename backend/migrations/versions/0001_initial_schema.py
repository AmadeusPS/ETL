"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-26
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cognito_sub", sa.String(128), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255)),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_users_cognito_sub", "users", ["cognito_sub"])
    op.create_index("ix_users_email", "users", ["email"])

    # subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("plan", sa.Enum("basic", "pro", "enterprise", name="plantier"), nullable=False),
        sa.Column("status", sa.String(32), default="active", nullable=False),
        sa.Column("stripe_customer_id", sa.String(128)),
        sa.Column("stripe_subscription_id", sa.String(128)),
        sa.Column("current_period_start", sa.DateTime),
        sa.Column("current_period_end", sa.DateTime),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    # stores
    op.create_table(
        "stores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("base_url", sa.String(2048), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    # products
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sku", sa.String(128)),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("category", sa.String(128)),
        sa.Column("current_price", sa.Numeric(10, 2)),
        sa.Column("currency", sa.String(8), default="EUR"),
        sa.Column("target_margin", sa.Numeric(5, 2)),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    # competitor_products
    op.create_table(
        "competitor_products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("name", sa.String(512)),
        sa.Column("sku", sa.String(128)),
        sa.Column("current_price", sa.Numeric(10, 2)),
        sa.Column("previous_price", sa.Numeric(10, 2)),
        sa.Column("currency", sa.String(8), default="EUR"),
        sa.Column("in_stock", sa.Boolean),
        sa.Column("image_url", sa.String(2048)),
        sa.Column("last_scraped_at", sa.DateTime),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    # price_snapshots
    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("competitor_product_id", sa.Integer, sa.ForeignKey("competitor_products.id"), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(8), default="EUR"),
        sa.Column("scraped_at", sa.DateTime, nullable=False, index=True),
    )
    op.create_index("ix_price_snapshots_scraped_at", "price_snapshots", ["scraped_at"])

    # alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id")),
        sa.Column("competitor_product_id", sa.Integer, sa.ForeignKey("competitor_products.id")),
        sa.Column(
            "alert_type",
            sa.Enum("price_drop", "price_increase", "new_product", "out_of_stock", "back_in_stock", name="alerttype"),
            nullable=False,
        ),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("is_read", sa.Boolean, default=False, nullable=False),
        sa.Column("sent_email", sa.Boolean, default=False, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, index=True),
    )
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])

    # ai_recommendations
    op.create_table(
        "ai_recommendations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("context_input", sa.Text, nullable=False),
        sa.Column("claude_output", sa.Text, nullable=False),
        sa.Column("suggested_price", sa.Numeric(10, 2)),
        sa.Column("reasoning", sa.Text),
        sa.Column(
            "status",
            sa.Enum("pending", "accepted", "rejected", "applied", name="recommendationstatus"),
            default="pending",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("reviewed_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("ai_recommendations")
    op.drop_table("alerts")
    op.drop_table("price_snapshots")
    op.drop_table("competitor_products")
    op.drop_table("products")
    op.drop_table("stores")
    op.drop_table("subscriptions")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS plantier")
    op.execute("DROP TYPE IF EXISTS alerttype")
    op.execute("DROP TYPE IF EXISTS recommendationstatus")
