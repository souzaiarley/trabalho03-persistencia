from beanie import Document, Link
from pydantic import BaseModel
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .autor import Autor
    from .emprestimo import Emprestimo

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
    id: str
    titulo: str
    ano: int
    isbn: str
    categoria: Optional[str]

    model_config = {
        "from_attributes": True
    }
