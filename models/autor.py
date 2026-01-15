from beanie import Document, Link
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .livro import Livro

class Autor(Document):
    nome: str
    nacionalidade: Optional[str]
    ano_nascimento: Optional[int]

    livros: Optional[List[Link["Livro"]]] = []

    class Settings:
        name = "autores"
