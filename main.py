from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

# Ganti dengan connection string kamu
MONGODB_URL = "mongodb+srv://alandwinanda:Takako88@cluster0.3i1vuxk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    app.mongodb = app.mongodb_client["mydatabase"]
    yield
    # Shutdown
    app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)


class Item(BaseModel):
    name: str
    description: str
    data: str

@app.post("/items/")
async def create_item(item: Item):
    result = await app.mongodb["items"].insert_one(item.model_dump())
    return {"id": str(result.inserted_id)}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    item = await app.mongodb["items"].find_one({"name": item_id}, {'_id': 0})
    return item

@app.get("/items/")
async def search_items(name: str = Query(None, title="Name to search for")):
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    
    cursor = app.mongodb["items"].find(query)
    items = await cursor.to_list(length=100)
    return [Item(**item) for item in items]