from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import home, alunos, autores, livros, emprestimos
# from routes import autores, livros, emprestimos, estatisticas
from database import init_db, close_db
from fastapi_pagination import add_pagination

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)

app.include_router(home.router)
app.include_router(alunos.router)
app.include_router(autores.router)
app.include_router(livros.router)
app.include_router(emprestimos.router)
# app.include_router(estatisticas.router)
add_pagination(app)
