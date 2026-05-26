# models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    Boolean,
    TIMESTAMP,
    ForeignKey
)

from sqlalchemy.sql import func
from database import Base


# PRODUCTS TABLE
class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String, unique=True, nullable=False)
    brand = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    icon = Column(String)
    base_price = Column(Float, nullable=False)
    spec = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


# STORE MAPPINGS TABLE
class StoreMapping(Base):
    __tablename__ = "store_mappings"

    mapping_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    store_name = Column(String, nullable=False)
    store_product_id = Column(String, nullable=False)
    store_url = Column(Text, nullable=False)
    matched_by = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())


# STORE PRICES TABLE
class StorePrice(Base):
    __tablename__ = "store_prices"

    price_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    store_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    discount_pct = Column(Float)
    in_stock = Column(Boolean)
    is_lowest = Column(Boolean)
    fetched_at = Column(TIMESTAMP, server_default=func.now())


# USERS TABLE
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


# BROWSING HISTORY TABLE
class BrowsingHistory(Base):
    __tablename__ = "browsing_history"

    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    view_count = Column(Integer, default=1)
    last_viewed = Column(TIMESTAMP, server_default=func.now())


# CHAT HISTORY TABLE
class ChatHistory(Base):
    __tablename__ = "chat_history"

    chat_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    role = Column(String, nullable=False, default="user")
    message = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP, server_default=func.now())