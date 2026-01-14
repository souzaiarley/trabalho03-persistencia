from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .aluno import Aluno
    from .livro import Livro

class EmprestimoBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    data_emprestimo: date
    data_devolucao_prevista: date
    data_devolucao: date | None = Field(default=None)

class Emprestimo(EmprestimoBase, table=True):
    """Modelo de empréstimo de livro"""
    aluno_id: int = Field(foreign_key='aluno.id')
    livro_id: int = Field(foreign_key='livro.id')

    aluno: 'Aluno' = Relationship(back_populates='emprestimos')
    livro: 'Livro' = Relationship(back_populates='emprestimos')

class EmprestimoInput(EmprestimoBase):
    aluno_id: int
    livro_id: int

class EmprestimoWithLivro(EmprestimoBase):
    livro: 'Livro'

class EmprestimoWithAluno(EmprestimoBase):
    aluno: 'Aluno'

class EmprestimoFull(EmprestimoBase):
    aluno: 'Aluno'
    livro: 'Livro'