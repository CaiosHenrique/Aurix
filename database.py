import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

def get_champions_collection():
    MONGO_URI = os.getenv('MONGO_URI')
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.Aurix_db
    return db.champions