from fastapi import APIRouter, HTTPException, Query
from beanie import PydanticObjectId, Link
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from typing import List, Optional
from models.livro import Livro, LivroCreate, LivroUpdate, LivroOut, LivroComEstatisticas
from models.autor import Autor
from models.emprestimo import Emprestimo, EmprestimoFull, EmprestimoWithLivroOut
from models.aluno import AlunoOut

router = APIRouter(
    prefix="/livros",
    tags=["livros"]
)

@router.post("/", response_model=Livro)
async def create_livro(livro_data: LivroCreate):
    """Cria um novo livro."""
    livro = Livro(**livro_data.model_dump())
    await livro.insert()
    return livro

@router.get("/", response_model=Page[Livro])
async def read_livros():
    """Retorna uma lista de livros com paginação."""
    return await apaginate(Livro)

@router.get("/{livro_id}", response_model=Livro)
async def read_livro(livro_id: PydanticObjectId):
    """Retorna um livro pelo ID."""
    livro = await Livro.get(livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro

@router.put("/{livro_id}", response_model=Livro)
async def update_livro(livro_id: PydanticObjectId, livro_data: LivroUpdate):
    """Atualiza os dados de um livro pelo ID."""
    livro = await Livro.get(livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    await livro.set(livro_data.model_dump(exclude_unset=True))
    return livro

@router.delete("/{livro_id}")
async def delete_livro(livro_id: PydanticObjectId):
    """Deleta um livro pelo ID."""
    livro = await Livro.get(livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    await livro.delete()
    return {"detail": "Livro deletado com sucesso"}


# Relacionamento com autores

@router.post("/{livro_id}/autores/{autor_id}")
async def add_autor_to_livro(livro_id: PydanticObjectId, autor_id: PydanticObjectId):
    """Vincula um autor a um livro."""
    livro = await Livro.get(livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    autor = await Autor.get(autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    # Inicializa listas se estiverem None
    if livro.autores is None:
        livro.autores = []
    if autor.livros is None:
        autor.livros = []

    # Verifica se já está vinculado
    if any(link.ref.id == autor_id for link in livro.autores):
        raise HTTPException(status_code=400, detail="Autor já está vinculado a este livro")

    livro.autores.append(autor)
    autor.livros.append(livro)
    
    await livro.save()
    await autor.save()
    
    return {"detail": "Autor adicionado ao livro com sucesso"}

@router.get("/{livro_id}/autores", response_model=List[Autor])
async def get_autores_of_livro(livro_id: PydanticObjectId):
    """Retorna os autores associados a um livro."""
    livro = await Livro.get(livro_id, fetch_links=True)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro.autores or []

@router.delete("/{livro_id}/autores/{autor_id}")
async def remove_autor_from_livro(livro_id: PydanticObjectId, autor_id: PydanticObjectId):
    """Remove o vínculo de um autor com um livro."""
    livro = await Livro.get(livro_id, fetch_links=True)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    autor = await Autor.get(autor_id, fetch_links=True)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    if livro.autores:
        livro.autores = [a for a in livro.autores if a.id != autor_id]
        await livro.save()
    
    if autor.livros:
        autor.livros = [l for l in autor.livros if l.id != livro_id]
        await autor.save()

    return {"detail": "Autor removido do livro com sucesso"}


# Relacionamento com emprestimos

@router.get("/{livro_id}/emprestimos", response_model=Page[EmprestimoFull])
async def get_emprestimos_of_livro(livro_id: PydanticObjectId):  
    """Retorna os empréstimos de um livro."""
    livro = await Livro.get(livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    query = Emprestimo.find(Emprestimo.livro.id == livro_id).fetch_links()

    async def transform(emp):
        return EmprestimoFull(
            id=str(emp.id),
            data_emprestimo=emp.data_emprestimo,
            data_devolucao_prevista=emp.data_devolucao_prevista,
            data_devolucao=emp.data_devolucao,
            aluno=AlunoOut(
                id=str(emp.aluno.id),
                nome=emp.aluno.nome,
                matricula=emp.aluno.matricula,
                curso=emp.aluno.curso,
                email=emp.aluno.email
            ),
            livro=LivroOut(
                id=str(emp.livro.id),
                titulo=emp.livro.titulo,
                ano=emp.livro.ano,
                isbn=emp.livro.isbn,
                categoria=emp.livro.categoria
            )
        )

    return await apaginate(query, transform=transform)


# Consultas complexas

@router.get("/buscar/query", response_model=Page[Livro])
async def buscar_livros(
    q: str = Query(..., description="Termo de busca (título ou categoria)")
):
    """Busca livros por título ou categoria."""
    query = Livro.find({
        "$or": [
            {"titulo": {"$regex": q, "$options": "i"}},
            {"categoria": {"$regex": q, "$options": "i"}}
        ]
    })
    return await apaginate(query)


@router.get("/mais-emprestados/ranking", response_model=List[LivroComEstatisticas])
async def get_livros_mais_emprestados(
    limit: int = Query(default=10, le=50, description="Número de livros a retornar")
):
    """
    Retorna os livros mais emprestados com estatísticas.
    """
    # Agregação para contar empréstimos por livro
    pipeline = [
        {
            "$group": {
                "_id": "$livro.$id",
                "total_emprestimos": {"$sum": 1},
                "emprestimos_ativos": {
                    "$sum": {
                        "$cond": [{"$eq": ["$data_devolucao", None]}, 1, 0]
                    }
                }
            }
        },
        {"$sort": {"total_emprestimos": -1}},
        {"$limit": limit}
    ]
    
    stats = await Emprestimo.aggregate(pipeline).to_list()
    
    livros_com_stats = []
    for stat in stats:
        livro = await Livro.get(stat["_id"])
        if livro:
            livro_dict = livro.model_dump()
            livro_dict["id"] = str(livro.id)
            livro_dict["total_emprestimos"] = stat["total_emprestimos"]
            livro_dict["emprestimos_ativos"] = stat["emprestimos_ativos"]
            livros_com_stats.append(LivroComEstatisticas(**livro_dict))
            
    return livros_com_stats


@router.get("/por-categoria/filtrar", response_model=Page[Livro])
async def get_livros_por_categoria(
    categoria: str = Query(..., description="Nome da categoria")
):
    """Filtra livros por categoria."""
    query = Livro.find({"categoria": {"$regex": categoria, "$options": "i"}})
    return await apaginate(query)