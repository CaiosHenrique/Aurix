import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

def get_champions_collection():
    MONGO_URI = os.getenv('MONGO_URI')
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.Aurix_db
    return db.champions

try:
    champions_collection = get_champions_collection()
    print("Conexão com o banco de dados estabelecida com sucesso.")
except Exception as e:
    print(f"Error ao conectar ao banco de dados: {e}")