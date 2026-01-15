from .aluno import *
from .autor import *
from .emprestimo import *
from .livro import *

Autor.model_rebuild()
Livro.model_rebuild()
Emprestimo.model_rebuild()

__all__ = ["Aluno", "Autor", "Emprestimo", "Livro"]
