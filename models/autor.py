from beanie import Document, Link
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from .livro import Livro

class AutorCreate(BaseModel):
    nome: str
    nacionalidade: Optional[str] = None
    ano_nascimento: Optional[int] = None

class AutorUpdate(BaseModel):
    nome: Optional[str] = None
    nacionalidade: Optional[str] = None
    ano_nascimento: Optional[int] = None

class Autor(Document):
    nome: str
    nacionalidade: Optional[str]
    ano_nascimento: Optional[int]

    livros: Optional[List[Link["Livro"]]] = []

    class Settings:
        name = "autores"
