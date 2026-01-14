from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from pydantic import BaseModel
from models.aluno import Aluno
from models.autor import Autor
from models.livro import Livro
from models.emprestimo import Emprestimo
from database import get_session
from datetime import date

router = APIRouter(
    prefix="/estatisticas",
    tags=["estatisticas"]
)


class EstatisticasGerais(BaseModel):
    """Modelo para estatísticas gerais do sistema"""
    total_alunos: int
    total_autores: int
    total_livros: int
    total_emprestimos: int
    emprestimos_ativos: int
    emprestimos_finalizados: int
    emprestimos_atrasados: int
    livro_mais_emprestado: str | None
    aluno_mais_ativo: str | None


@router.get("/", response_model=EstatisticasGerais)
def get_estatisticas_gerais(session: Session = Depends(get_session)):
    """
    Retorna estatísticas gerais do sistema de biblioteca.
    """
    # Contadores básicos
    total_alunos = len(session.exec(select(Aluno)).all())
    total_autores = len(session.exec(select(Autor)).all())
    total_livros = len(session.exec(select(Livro)).all())
    total_emprestimos = len(session.exec(select(Emprestimo)).all())

    # Empréstimos ativos
    emprestimos_ativos = len(
        session.exec(
            select(Emprestimo).where(Emprestimo.data_devolucao == None)
        ).all()
    )

    # Empréstimos finalizados
    emprestimos_finalizados = total_emprestimos - emprestimos_ativos

    # Empréstimos atrasados
    hoje = date.today()
    emprestimos_atrasados = len(
        session.exec(
            select(Emprestimo)
            .where(
                (Emprestimo.data_devolucao == None) &
                (Emprestimo.data_devolucao_prevista < hoje)
            )
        ).all()
    )

    # Livro mais emprestado
    livro_mais_emprestado_query = (
        select(Livro.titulo, func.count(Emprestimo.id).label('total'))
        .join(Emprestimo, Livro.id == Emprestimo.livro_id)
        .group_by(Livro.id)
        .order_by(func.count(Emprestimo.id).desc())
        .limit(1)
    )
    result = session.exec(livro_mais_emprestado_query).first()
    livro_mais_emprestado = result[0] if result else None

    # Aluno mais ativo
    aluno_mais_ativo_query = (
        select(Aluno.nome, func.count(Emprestimo.id).label('total'))
        .join(Emprestimo, Aluno.id == Emprestimo.aluno_id)
        .group_by(Aluno.id)
        .order_by(func.count(Emprestimo.id).desc())
        .limit(1)
    )
    result = session.exec(aluno_mais_ativo_query).first()
    aluno_mais_ativo = result[0] if result else None

    return EstatisticasGerais(
        total_alunos=total_alunos,
        total_autores=total_autores,
        total_livros=total_livros,
        total_emprestimos=total_emprestimos,
        emprestimos_ativos=emprestimos_ativos,
        emprestimos_finalizados=emprestimos_finalizados,
        emprestimos_atrasados=emprestimos_atrasados,
        livro_mais_emprestado=livro_mais_emprestado,
        aluno_mais_ativo=aluno_mais_ativo
    )
