from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .autor import Autor
    from .emprestimo import Emprestimo

class LivroCreate(BaseModel):
    titulo: str
    ano: int
    isbn: str
    categoria: Optional[str] = None

class LivroUpdate(BaseModel):
    titulo: Optional[str] = None
    ano: Optional[int] = None
    isbn: Optional[str] = None
    categoria: Optional[str] = None

class Livro(Document):
    titulo: str
    ano: int
    isbn: str
    categoria: Optional[str]

    emprestimos: Optional[List[Link["Emprestimo"]]] = []
    autores: Optional[List[Link["Autor"]]] = []

    class Settings:
        name = "livros"

class LivroOut(BaseModel):
    id: PydanticObjectId
    titulo: str
    ano: int
    isbn: str
    categoria: Optional[str]

    model_config = {
        "from_attributes": True
    }

class LivroComEstatisticas(LivroOut):
    total_emprestimos: int = 0
    emprestimos_ativos: int = 0
