from pymongo import AsyncMongoClient
from beanie import init_beanie
from models import Aluno, Autor, Emprestimo, Livro
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DB_NAME")

async def init_db():
    global _client
    _client = AsyncMongoClient(DATABASE_URL)
    db = _client[DB_NAME]

    await init_beanie(
        database=db,
        document_models=[
            Aluno,
            Autor,
            Emprestimo,
            Livro,
        ],
    )

async def close_db():
    global _client
    if _client is not None:
        await _client.close()
        _client = None
