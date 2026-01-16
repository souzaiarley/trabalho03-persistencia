from beanie import Document, Link
from pydantic import BaseModel
from datetime import date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .aluno import Aluno, AlunoOut
    from .livro import Livro, LivroOut

class EmprestimoCreate(BaseModel):
    data_emprestimo: date
    data_devolucao_prevista: date
    data_devolucao: Optional[date] = None
    aluno_id: str
    livro_id: str

class EmprestimoUpdate(BaseModel):
    data_emprestimo: Optional[date] = None
    data_devolucao_prevista: Optional[date] = None
    data_devolucao: Optional[date] = None
    aluno_id: Optional[str] = None
    livro_id: Optional[str] = None

class Emprestimo(Document):
    data_emprestimo: date
    data_devolucao_prevista: date
    data_devolucao: Optional[date] = None

    aluno: Link["Aluno"]
    livro: Link["Livro"]

    class Settings:
        name = "emprestimos"

class EmprestimoWithLivroOut(BaseModel):
    id: str
    data_emprestimo: date
    data_devolucao_prevista: date
    data_devolucao: Optional[date]
    livro: "LivroOut"

    model_config = {
        "from_attributes": True
    }

class EmprestimoFull(BaseModel):
    id: str
    data_emprestimo: date
    data_devolucao_prevista: date
    data_devolucao: Optional[date]
    aluno: "AlunoOut"
    livro: "LivroOut"

    model_config = {
        "from_attributes": True
    }
