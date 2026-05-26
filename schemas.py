from pydantic import BaseModel, field_validator
# =========================================================
# PRODUCT SCHEMA
# =========================================================

class ProductCreate(BaseModel):

    canonical_name: str
    brand: str
    category: str
    subcategory: str
    icon: str
    base_price: float
    spec: str

    @field_validator("canonical_name")
    def validate_name(cls, value):

        if not value.strip():
            raise ValueError("Product name cannot be empty")

        return value

    @field_validator("brand")
    def validate_brand(cls, value):

        if not value.strip():
            raise ValueError("Brand name cannot be empty")

        return value

    @field_validator("base_price")
    def validate_price(cls, value):

        if value <= 0:
            raise ValueError("Price must be greater than 0")

        return value
    
# STORE MAPPING SCHEMA
class StoreMappingCreate(BaseModel):

    product_id: int
    store_name: str
    store_product_id: str
    store_url: str
    matched_by: str

    @field_validator("store_name")
    def validate_store_name(cls, value):

        if not value.strip():
            raise ValueError("Store name cannot be empty")

        return value

    @field_validator("store_url")
    def validate_url(cls, value):

        if not value.strip():
            raise ValueError("Store URL cannot be empty")

        return value


# STORE PRICE SCHEMA
class StorePriceCreate(BaseModel):

    product_id: int
    store_name: str
    price: float
    original_price: float
    discount_pct: float
    in_stock: bool
    is_lowest: bool

    @field_validator("price")
    def validate_price(cls, value):

        if value <= 0:
            raise ValueError("Price must be greater than 0")

        return value

# USER SCHEMA

class UserCreate(BaseModel):

    name: str

    @field_validator("name")
    def validate_name(cls, value):

        if not value.strip():
            raise ValueError("User name cannot be empty")

        return value

# BROWSING HISTORY SCHEMA
class BrowsingHistoryCreate(BaseModel):

    user_id: int
    product_id: int
    view_count: int

    @field_validator("view_count")
    def validate_view_count(cls, value):

        if value <= 0:
            raise ValueError("View count must be greater than 0")

        return value

# CHAT HISTORY SCHEMA
class ChatHistoryCreate(BaseModel):

    user_id: int
    message: str

    @field_validator("message")
    def validate_message(cls, value):

        if not value.strip():
            raise ValueError("Message cannot be empty")

        return value