# main.py
# Full ShopBot AI Backend

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import (
    Base,
    Product,
    StoreMapping,
    StorePrice,
    User,
    BrowsingHistory,
    ChatHistory
)
from schemas import (
    ProductCreate,
    StoreMappingCreate,
    StorePriceCreate,
    UserCreate,
    BrowsingHistoryCreate,
    ChatHistoryCreate
)
import os
import httpx
from google import genai
from google.genai import types
from bs4 import BeautifulSoup
from pydantic import BaseModel


# CREATE TABLES
Base.metadata.create_all(bind=engine)


# FASTAPI APP
app = FastAPI(
    title="ShopBot AI API",
    description="Multi-Agent AI Shopping Assistant Backend",
    version="1.0.0"
)


# DATABASE CONNECTION
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# HOME
@app.get("/", tags=["Home"])

def home():

    return {
        "message": "ShopBot API Running"
    }


# PRODUCTS CRUD

@app.post("/products", tags=["Products"])

def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    existing_product = db.query(Product).filter(
        Product.canonical_name == product.canonical_name
    ).first()

    if existing_product:

        raise HTTPException(
            status_code=400,
            detail="Product already exists"
        )

    new_product = Product(**product.dict())

    db.add(new_product)

    db.commit()

    db.refresh(new_product)

    return {
        "message": "Product created successfully",
        "data": new_product
    }


@app.get("/products", tags=["Products"])

def get_products(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:

        raise HTTPException(
            status_code=404,
            detail="No products found"
        )

    return products


@app.put("/products/{product_id}", tags=["Products"])

def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    existing_product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not existing_product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_product.canonical_name = product.canonical_name
    existing_product.brand = product.brand
    existing_product.category = product.category
    existing_product.subcategory = product.subcategory
    existing_product.icon = product.icon
    existing_product.base_price = product.base_price
    existing_product.spec = product.spec

    db.commit()

    return {
        "message": "Product updated successfully"
    }


@app.delete("/products/{product_id}", tags=["Products"])

def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)

    db.commit()

    return {
        "message": "Product deleted successfully"
    }


# STORE MAPPINGS CRUD

@app.post("/store-mappings", tags=["Store Mappings"])

def create_store_mapping(
    mapping: StoreMappingCreate,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.product_id == mapping.product_id
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product does not exist"
        )

    new_mapping = StoreMapping(**mapping.dict())

    db.add(new_mapping)

    db.commit()

    db.refresh(new_mapping)

    return {
        "message": "Store mapping created successfully",
        "data": new_mapping
    }


@app.get("/store-mappings", tags=["Store Mappings"])

def get_store_mappings(
    db: Session = Depends(get_db)
):

    mappings = db.query(StoreMapping).all()

    if not mappings:

        raise HTTPException(
            status_code=404,
            detail="No store mappings found"
        )

    return mappings


@app.put("/store-mappings/{mapping_id}", tags=["Store Mappings"])

def update_store_mapping(
    mapping_id: int,
    mapping: StoreMappingCreate,
    db: Session = Depends(get_db)
):

    existing_mapping = db.query(StoreMapping).filter(
        StoreMapping.mapping_id == mapping_id
    ).first()

    if not existing_mapping:

        raise HTTPException(
            status_code=404,
            detail="Store mapping not found"
        )

    existing_mapping.product_id = mapping.product_id
    existing_mapping.store_name = mapping.store_name
    existing_mapping.store_product_id = mapping.store_product_id
    existing_mapping.store_url = mapping.store_url
    existing_mapping.matched_by = mapping.matched_by

    db.commit()

    return {
        "message": "Store mapping updated successfully"
    }


@app.delete("/store-mappings/{mapping_id}", tags=["Store Mappings"])

def delete_store_mapping(
    mapping_id: int,
    db: Session = Depends(get_db)
):

    mapping = db.query(StoreMapping).filter(
        StoreMapping.mapping_id == mapping_id
    ).first()

    if not mapping:

        raise HTTPException(
            status_code=404,
            detail="Store mapping not found"
        )

    db.delete(mapping)

    db.commit()

    return {
        "message": "Store mapping deleted successfully"
    }


# STORE PRICES CRUD

@app.post("/store-prices", tags=["Store Prices"])

def create_store_price(
    price: StorePriceCreate,
    db: Session = Depends(get_db)
):

    if price.price <= 0:

        raise HTTPException(
            status_code=400,
            detail="Price must be greater than 0"
        )

    product = db.query(Product).filter(
        Product.product_id == price.product_id
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product does not exist"
        )

    new_price = StorePrice(**price.dict())

    db.add(new_price)

    db.commit()

    db.refresh(new_price)

    return {
        "message": "Store price added successfully",
        "data": new_price
    }


@app.get("/store-prices", tags=["Store Prices"])

def get_store_prices(
    db: Session = Depends(get_db)
):

    prices = db.query(StorePrice).all()

    if not prices:

        raise HTTPException(
            status_code=404,
            detail="No store prices found"
        )

    return prices


@app.put("/store-prices/{price_id}", tags=["Store Prices"])

def update_store_price(
    price_id: int,
    price: StorePriceCreate,
    db: Session = Depends(get_db)
):

    existing_price = db.query(StorePrice).filter(
        StorePrice.price_id == price_id
    ).first()

    if not existing_price:

        raise HTTPException(
            status_code=404,
            detail="Store price not found"
        )

    existing_price.product_id = price.product_id
    existing_price.store_name = price.store_name
    existing_price.price = price.price
    existing_price.original_price = price.original_price
    existing_price.discount_pct = price.discount_pct
    existing_price.in_stock = price.in_stock
    existing_price.is_lowest = price.is_lowest

    db.commit()

    return {
        "message": "Store price updated successfully"
    }


@app.delete("/store-prices/{price_id}", tags=["Store Prices"])

def delete_store_price(
    price_id: int,
    db: Session = Depends(get_db)
):

    price = db.query(StorePrice).filter(
        StorePrice.price_id == price_id
    ).first()

    if not price:

        raise HTTPException(
            status_code=404,
            detail="Store price not found"
        )

    db.delete(price)

    db.commit()

    return {
        "message": "Store price deleted successfully"
    }


# USERS CRUD

@app.post("/users", tags=["Users"])

def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.name == user.name
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    new_user = User(**user.dict())

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "data": new_user
    }


@app.get("/users", tags=["Users"])

def get_users(
    db: Session = Depends(get_db)
):

    users = db.query(User).all()

    if not users:

        raise HTTPException(
            status_code=404,
            detail="No users found"
        )

    return users


# BROWSING HISTORY CRUD

@app.post("/browsing-history", tags=["Browsing History"])

def create_browsing_history(
    history: BrowsingHistoryCreate,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == history.user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User does not exist"
        )

    product = db.query(Product).filter(
        Product.product_id == history.product_id
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product does not exist"
        )

    new_history = BrowsingHistory(**history.dict())

    db.add(new_history)

    db.commit()

    db.refresh(new_history)

    return {
        "message": "Browsing history added successfully",
        "data": new_history
    }


@app.get("/browsing-history", tags=["Browsing History"])

def get_browsing_history(
    db: Session = Depends(get_db)
):

    history = db.query(BrowsingHistory).all()

    if not history:

        raise HTTPException(
            status_code=404,
            detail="No browsing history found"
        )

    return history


# CHAT HISTORY CRUD

@app.post("/chat-history", tags=["Chat History"])

def create_chat_history(
    chat: ChatHistoryCreate,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == chat.user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User does not exist"
        )

    if not chat.message.strip():

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    new_chat = ChatHistory(**chat.dict())

    db.add(new_chat)

    db.commit()

    db.refresh(new_chat)

    return {
        "message": "Chat message added successfully",
        "data": new_chat
    }


@app.get("/chat-history", tags=["Chat History"])

def get_chat_history(
    db: Session = Depends(get_db)
):

    chats = db.query(ChatHistory).all()

    if not chats:

        raise HTTPException(
            status_code=404,
            detail="No chat history found"
        )

    return chats


# SCRAPER ROUTE

class ScrapeRequest(BaseModel):
    product_id: int
    amazon_url: str
    flipkart_url: str


@app.post("/scrape", tags=["Scraper"])

def scrape_prices(
    req: ScrapeRequest,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.product_id == req.product_id
    ).first()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product does not exist"
        )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    results = {}

    amazon_price_record = None
    flipkart_price_record = None

    # --- Scrape Amazon ---
    try:
        amazon_response = httpx.get(
            req.amazon_url,
            headers=headers,
            timeout=10,
            follow_redirects=True
        )
        amazon_soup = BeautifulSoup(amazon_response.text, "html.parser")

        amazon_price_tag = (
            amazon_soup.select_one("span#priceblock_ourprice") or
            amazon_soup.select_one("span.a-offscreen") or
            amazon_soup.select_one("span.a-price-whole")
        )

        if amazon_price_tag:
            raw = amazon_price_tag.get_text(strip=True)
            cleaned = ''.join(c for c in raw if c.isdigit() or c == '.')
            amazon_price = float(cleaned) if cleaned else None
        else:
            amazon_price = None

    except Exception:
        amazon_price = None

    if amazon_price:
        amazon_price_record = StorePrice(
            product_id=req.product_id,
            store_name="amazon",
            price=amazon_price,
            original_price=amazon_price,
            discount_pct=0.0,
            in_stock=True,
            is_lowest=False
        )
        db.add(amazon_price_record)

    results["amazon"] = {
        "url": req.amazon_url,
        "price": amazon_price if amazon_price else "Could not scrape"
    }

    # --- Scrape Flipkart ---
    try:
        flipkart_response = httpx.get(
            req.flipkart_url,
            headers=headers,
            timeout=10,
            follow_redirects=True
        )
        flipkart_soup = BeautifulSoup(flipkart_response.text, "html.parser")

        flipkart_price_tag = (
            flipkart_soup.select_one("div._30jeq3") or
            flipkart_soup.select_one("div._16Jk6d") or
            flipkart_soup.select_one("div.Nx9bqj")
        )

        if flipkart_price_tag:
            raw = flipkart_price_tag.get_text(strip=True)
            cleaned = ''.join(c for c in raw if c.isdigit() or c == '.')
            flipkart_price = float(cleaned) if cleaned else None
        else:
            flipkart_price = None

    except Exception:
        flipkart_price = None

    if flipkart_price:
        flipkart_price_record = StorePrice(
            product_id=req.product_id,
            store_name="flipkart",
            price=flipkart_price,
            original_price=flipkart_price,
            discount_pct=0.0,
            in_stock=True,
            is_lowest=False
        )
        db.add(flipkart_price_record)

    results["flipkart"] = {
        "url": req.flipkart_url,
        "price": flipkart_price if flipkart_price else "Could not scrape"
    }

    # Mark cheapest store
    if amazon_price and flipkart_price:
        if amazon_price <= flipkart_price:
            amazon_price_record.is_lowest = True
        else:
            flipkart_price_record.is_lowest = True

    db.commit()

    return {
        "message": "Scraping complete",
        "product_id": req.product_id,
        "results": results,
        "cheapest": (
            "amazon" if (amazon_price and flipkart_price and amazon_price <= flipkart_price)
            else "flipkart" if flipkart_price
            else "unknown"
        )
    }


# AI CHAT ROUTE

class AIChatRequest(BaseModel):
    user_id: int
    message: str


@app.post("/ai-chat", tags=["AI Chat"])

def ai_chat(
    req: AIChatRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == req.user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User does not exist"
        )

    if not req.message.strip():

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    # Fetch last 10 messages for context
    past_messages = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == req.user_id)
        .order_by(ChatHistory.chat_id.desc())
        .limit(10)
        .all()
    )

    past_messages = list(reversed(past_messages))

    # Build conversation history for Gemini
    contents = []

    for msg in past_messages:
        contents.append(
            types.Content(
                role="user" if msg.role == "user" else "model",
                parts=[types.Part(text=msg.message)]
            )
        )

    # Add current user message
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text=req.message)]
        )
    )

    # Call Gemini API
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are ShopBot, an AI shopping assistant. "
                    "You help users compare product prices between Amazon and Flipkart, "
                    "explain pros and cons of products, suggest similar products, "
                    "and help users make smart buying decisions. "
                    "Be concise, helpful, and friendly."
                ),
                max_output_tokens=500,
                temperature=0.7
            )
        )

        ai_reply = response.text

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI API error: {str(e)}"
        )

    # Save user message
    user_message_record = ChatHistory(
        user_id=req.user_id,
        role="user",
        message=req.message
    )
    db.add(user_message_record)

    # Save AI reply
    ai_message_record = ChatHistory(
        user_id=req.user_id,
        role="assistant",
        message=ai_reply
    )
    db.add(ai_message_record)

    db.commit()

    return {
        "message": "AI response generated",
        "user_id": req.user_id,
        "user_message": req.message,
        "ai_reply": ai_reply
    }