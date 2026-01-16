from fastapi import APIRouter
from pydantic import BaseModel
from datetime import date
from models.aluno import Aluno
from models.autor import Autor
from models.livro import Livro
from models.emprestimo import Emprestimo

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
async def get_estatisticas_gerais():
    """
    Retorna estatísticas gerais do sistema de biblioteca (Versão NoSQL).
    """
    total_alunos = await Aluno.count()
    total_autores = await Autor.count()
    total_livros = await Livro.count()
    total_emprestimos = await Emprestimo.count()

    emprestimos_ativos = await Emprestimo.find(
        Emprestimo.data_devolucao == None
    ).count()

    emprestimos_finalizados = total_emprestimos - emprestimos_ativos

    hoje = date.today()
    emprestimos_atrasados = await Emprestimo.find(
        Emprestimo.data_devolucao == None,
        Emprestimo.data_devolucao_prevista < hoje
    ).count()

    pipeline_livro = [
        {"$group": {"_id": "$livro.$id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    
    top_livro_data = await Emprestimo.aggregate(pipeline_livro).to_list(1)
    
    livro_mais_emprestado = None
    if top_livro_data:
        livro_id = top_livro_data[0]["_id"]
        livro = await Livro.get(livro_id)
        if livro:
            livro_mais_emprestado = livro.titulo

    pipeline_aluno = [
        {"$group": {"_id": "$aluno.$id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]

    top_aluno_data = await Emprestimo.aggregate(pipeline_aluno).to_list(1)

    aluno_mais_ativo = None
    if top_aluno_data:
        aluno_id = top_aluno_data[0]["_id"]
        aluno = await Aluno.get(aluno_id)
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
