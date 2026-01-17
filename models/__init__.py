from .aluno import *
from .autor import *
from .emprestimo import *
from .livro import *

AlunoOut.model_rebuild()
Autor.model_rebuild()
Livro.model_rebuild()
LivroOut.model_rebuild()
Emprestimo.model_rebuild()
EmprestimoWithLivroOut.model_rebuild()
EmprestimoFull.model_rebuild()