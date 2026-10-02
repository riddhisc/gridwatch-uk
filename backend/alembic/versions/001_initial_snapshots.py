from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial_snapshots"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "carbon_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("period_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_to", sa.DateTime(timezone=True), nullable=False),
        sa.Column("region_code", sa.String(length=32), nullable=False, server_default="GB"),
        sa.Column("region_name", sa.String(length=128), nullable=True),
        sa.Column("forecast_intensity", sa.Integer(), nullable=True),
        sa.Column("actual_intensity", sa.Integer(), nullable=True),
        sa.Column("intensity_index", sa.String(length=32), nullable=True),
        sa.Column("generation_mix", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="neso_carbon_intensity"),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("period_from", "period_to", "region_code", name="uq_carbon_period_region"),
    )
    op.create_index("ix_carbon_snapshots_period_from", "carbon_snapshots", ["period_from"])
    op.create_index("ix_carbon_snapshots_region_period", "carbon_snapshots", ["region_code", "period_from"])

    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("period_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_to", sa.DateTime(timezone=True), nullable=False),
        sa.Column("product_code", sa.String(length=64), nullable=False),
        sa.Column("tariff_code", sa.String(length=128), nullable=False),
        sa.Column("gsp_region", sa.String(length=8), nullable=False),
        sa.Column("value_exc_vat", sa.Numeric(12, 6), nullable=False),
        sa.Column("value_inc_vat", sa.Numeric(12, 6), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="octopus_agile"),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("period_from", "period_to", "tariff_code", name="uq_price_period_tariff"),
    )
    op.create_index("ix_price_snapshots_period_from", "price_snapshots", ["period_from"])
    op.create_index("ix_price_snapshots_tariff_period", "price_snapshots", ["tariff_code", "period_from"])


def downgrade() -> None:
    op.drop_index("ix_price_snapshots_tariff_period", table_name="price_snapshots")
    op.drop_index("ix_price_snapshots_period_from", table_name="price_snapshots")
    op.drop_table("price_snapshots")
    op.drop_index("ix_carbon_snapshots_region_period", table_name="carbon_snapshots")
    op.drop_index("ix_carbon_snapshots_period_from", table_name="carbon_snapshots")
    op.drop_table("carbon_snapshots")
