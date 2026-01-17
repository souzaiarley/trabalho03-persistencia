from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .emprestimo import Emprestimo

class AlunoBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    matricula: str = Field(unique=True)
    curso: str
    email: str = Field(unique=True)

class Aluno(AlunoBase, table=True):
    """Modelo de aluno da biblioteca"""
    emprestimos: list['Emprestimo'] = Relationship(back_populates='aluno')