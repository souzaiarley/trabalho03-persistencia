import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.emprestimo import Emprestimo
from models.aluno import Aluno
from models.livro import Livro
from models.autor import Autor
import os
from dotenv import load_dotenv

load_dotenv()

async def diagnose():
    client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    db = client[os.getenv("DB_NAME")]
    await init_beanie(database=db, document_models=[Aluno, Autor, Emprestimo, Livro])
    
    q_emp = Emprestimo.find_all()
    q_livro = Livro.find_all()
    
    with open("results.txt", "w") as f:
        f.write(f"Emprestimo query type: {type(q_emp)}\n")
        f.write(f"Emprestimo has fetch_links: {hasattr(q_emp, 'fetch_links')}\n")
        if hasattr(q_emp, 'fetch_links'):
            f.write(f"Emprestimo fetch_links type: {type(getattr(q_emp, 'fetch_links'))}\n")
        
        f.write(f"Livro query type: {type(q_livro)}\n")
        f.write(f"Livro has fetch_links: {hasattr(q_livro, 'fetch_links')}\n")
        if hasattr(q_livro, 'fetch_links'):
            f.write(f"Livro fetch_links type: {type(getattr(q_livro, 'fetch_links'))}\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(diagnose())
