from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
from .livro_autor_link import LivroAutorLink

if TYPE_CHECKING:
    from .emprestimo import Emprestimo
    from .autor import Autor

class LivroBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str
    ano: int
    isbn: str = Field(unique=True)
    categoria: str

class Livro(LivroBase, table=True):
    """Modelo de livro da biblioteca"""
    emprestimos: list['Emprestimo'] = Relationship(back_populates='livro')
    autores: list['Autor'] = Relationship(
        back_populates='livros',
        link_model=LivroAutorLink
    )

class LivroComEstatisticas(LivroBase):
    """Livro com estatísticas de empréstimos"""
    total_emprestimos: int
    emprestimos_ativos: int