from fastapi import APIRouter
from pydantic import BaseModel
from models.aluno import Aluno
from models.autor import Autor
from models.livro import Livro
from models.emprestimo import Emprestimo
from datetime import date
from typing import Optional

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
    livro_mais_emprestado: Optional[str] = None
    aluno_mais_ativo: Optional[str] = None


@router.get("/", response_model=EstatisticasGerais)
async def get_estatisticas_gerais():
    """
    Retorna estatísticas gerais do sistema de biblioteca.
    """
    # Contadores básicos
    total_alunos = await Aluno.count()
    total_autores = await Autor.count()
    total_livros = await Livro.count()
    total_emprestimos = await Emprestimo.count()

    # Empréstimos ativos
    emprestimos_ativos = await Emprestimo.find(Emprestimo.data_devolucao == None).count()

    # Empréstimos finalizados
    emprestimos_finalizados = total_emprestimos - emprestimos_ativos

    # Empréstimos atrasados
    hoje = date.today()
    emprestimos_atrasados = await Emprestimo.find(
        Emprestimo.data_devolucao == None,
        Emprestimo.data_devolucao_prevista < hoje
    ).count()

    # Livro mais emprestado
    pipeline_livro = [
        {"$group": {"_id": "$livro.$id", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]
    res_livro = await Emprestimo.aggregate(pipeline_livro).to_list()
    livro_mais_emprestado = None
    if res_livro:
        livro = await Livro.get(res_livro[0]["_id"])
        if livro:
            livro_mais_emprestado = livro.titulo

    # Aluno mais ativo
    pipeline_aluno = [
        {"$group": {"_id": "$aluno.$id", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]
    res_aluno = await Emprestimo.aggregate(pipeline_aluno).to_list()
    aluno_mais_ativo = None
    if res_aluno:
        aluno = await Aluno.get(res_aluno[0]["_id"])
        if aluno:
            aluno_mais_ativo = aluno.nome

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
