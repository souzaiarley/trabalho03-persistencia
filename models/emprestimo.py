from beanie import Document, Link
from datetime import date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .aluno import Aluno
    from .livro import Livro

class Emprestimo(Document):
    data_emprestimo: date
    data_devolucao_prevista: date
    data_devolucao: Optional[date] = None

    aluno: Link["Aluno"]
    livro: Link["Livro"]

    class Settings:
        name = "emprestimos"
