import sqlalchemy as sa
from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Location(Base):
    __tablename__ = "locations"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    code = Column(Text, nullable=False, unique=True)
    name = Column(Text)


class SKU(Base):
    __tablename__ = "skus"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    sku_code = Column(Text, nullable=False, unique=True)
    title = Column(Text)
    description = Column(Text)


class SKUBarcode(Base):
    __tablename__ = "sku_barcodes"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    sku_id = Column(UUID(as_uuid=True), ForeignKey("skus.id", ondelete="CASCADE"))
    barcode = Column(Text, nullable=False, unique=True)
    sku = relationship("SKU", backref="barcodes")


class StockLedger(Base):
    __tablename__ = "stock_ledger"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    sku_id = Column(UUID(as_uuid=True), ForeignKey("skus.id", ondelete="CASCADE"))
    location_id = Column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="SET NULL")
    )
    on_hand = Column(BigInteger, default=0)
    reserved = Column(BigInteger, default=0)
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    __table_args__ = (
        UniqueConstraint("sku_id", "location_id", name="uix_sku_location"),
    )


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    sku_id = Column(UUID(as_uuid=True), ForeignKey("skus.id", ondelete="CASCADE"))
    location_id = Column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="SET NULL")
    )
    qty = Column(BigInteger, nullable=False)
    movement_type = Column(Text, nullable=False)
    barcode = Column(Text)
    batch = Column(Text)
    reference_id = Column(Text)
    created_by = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
