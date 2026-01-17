from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

from .livro_autor_link import LivroAutorLink

if TYPE_CHECKING:
    from .livro import Livro

class AutorBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    nacionalidade: str
    ano_nascimento: int

class Autor(AutorBase, table=True):
    """Modelo de autor de livros"""
    livros: list['Livro'] = Relationship(
        back_populates='autores',
        link_model=LivroAutorLink
    )