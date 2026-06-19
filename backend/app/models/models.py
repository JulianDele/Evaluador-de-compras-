"""
Modelos SQLAlchemy — definición de tablas de la base de datos.
"""
from datetime import date, time, datetime
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric, Date, Time,
    ForeignKey, DateTime, BigInteger, JSON, func, CheckConstraint,
    text, Computed
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String(200), nullable=False)
    email         = Column(String(320), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active     = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at    = Column(DateTime(timezone=True), nullable=False,
                           server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), nullable=False,
                           server_default=func.now(), onupdate=func.now())

    __table_args__ = ()

    purchases = relationship("Purchase", back_populates="user", cascade="all, delete-orphan")
    imports   = relationship("Import",   back_populates="uploader")
    audit_logs = relationship("AuditLog", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(300), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    purchases = relationship("Purchase", back_populates="product")


class Purchase(Base):
    __tablename__ = "purchases"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id     = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity       = Column(Integer, nullable=False)
    price          = Column(Numeric(12, 2), nullable=False)
    purchase_date  = Column(Date, nullable=False)
    purchase_time  = Column(Time, nullable=False)
    payment_method = Column(String(20), nullable=False)
    created_at     = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("quantity > 0",   name="ck_purchases_quantity"),
        CheckConstraint("price >= 0",     name="ck_purchases_price"),
        CheckConstraint(
            "payment_method IN ('Efectivo', 'Tarjeta', 'Transferencia')",
            name="ck_purchases_payment_method"
        ),
    )

    user    = relationship("User",    back_populates="purchases")
    product = relationship("Product", back_populates="purchases")

    @property
    def total(self) -> Decimal:
        return self.quantity * self.price


class Import(Base):
    __tablename__ = "imports"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    filename          = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size_bytes   = Column(Integer)
    uploader_user_id  = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    rows_detected     = Column(Integer, default=0)
    rows_imported     = Column(Integer, default=0)
    rows_skipped      = Column(Integer, default=0)
    status            = Column(String(20), nullable=False, default="pending",
                               server_default="pending")
    anonymized        = Column(Boolean, nullable=False, default=False)
    error_log         = Column(JSON)
    created_at        = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at      = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_imports_status"
        ),
    )

    uploader = relationship("User", back_populates="imports")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action      = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id   = Column(Integer)
    details     = Column(JSON)
    ip_address  = Column(String(45))
    created_at  = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
