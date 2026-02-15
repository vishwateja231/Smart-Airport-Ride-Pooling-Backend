"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    passenger_status = sa.Enum("waiting", "assigned", "cancelled", "completed", name="passengerstatus")
    cab_status = sa.Enum("available", "full", "offline", name="cabstatus")
    ride_status = sa.Enum("active", "cancelled", "completed", name="ridestatus")

    passenger_status.create(op.get_bind(), checkfirst=True)
    cab_status.create(op.get_bind(), checkfirst=True)
    ride_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "passengers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pickup_lat", sa.Float(), nullable=False),
        sa.Column("pickup_lng", sa.Float(), nullable=False),
        sa.Column("drop_lat", sa.Float(), nullable=False),
        sa.Column("drop_lng", sa.Float(), nullable=False),
        sa.Column("luggage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("detour_tolerance", sa.Float(), nullable=False, server_default="0.2"),
        sa.Column("status", passenger_status, nullable=False, server_default="waiting"),
    )
    op.create_index("idx_passenger_status", "passengers", ["status"])
    op.create_index("idx_passenger_pickup_lat", "passengers", ["pickup_lat"])
    op.create_index("idx_passenger_pickup_lng", "passengers", ["pickup_lng"])

    op.create_table(
        "cabs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("seat_capacity", sa.Integer(), nullable=False),
        sa.Column("luggage_capacity", sa.Integer(), nullable=False),
        sa.Column("status", cab_status, nullable=False, server_default="available"),
    )
    op.create_index("idx_cab_status", "cabs", ["status"])

    op.create_table(
        "rides",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cab_id", sa.Integer(), sa.ForeignKey("cabs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", ride_status, nullable=False, server_default="active"),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )
    op.create_index("idx_ride_status", "rides", ["status"])

    op.create_table(
        "ride_passengers",
        sa.Column("ride_id", sa.Integer(), sa.ForeignKey("rides.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("passenger_id", sa.Integer(), sa.ForeignKey("passengers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("pickup_order", sa.Integer(), nullable=False),
        sa.Column("drop_order", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ride_passengers")
    op.drop_index("idx_ride_status", table_name="rides")
    op.drop_table("rides")
    op.drop_index("idx_cab_status", table_name="cabs")
    op.drop_table("cabs")
    op.drop_index("idx_passenger_pickup_lng", table_name="passengers")
    op.drop_index("idx_passenger_pickup_lat", table_name="passengers")
    op.drop_index("idx_passenger_status", table_name="passengers")
    op.drop_table("passengers")
