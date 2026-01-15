from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from typing import List
from models.autor import Autor, AutorCreate, AutorUpdate
from models.livro import Livro

router = APIRouter(
    prefix="/autores",
    tags=["autores"]
)

@router.post("/", response_model=Autor)
async def create_autor(autor_data: AutorCreate):
    """Cria um novo autor."""
    autor = Autor(**autor_data.model_dump())
    await autor.insert()
    return autor

@router.get("/", response_model=Page[Autor])
async def read_autores():
    """Retorna uma lista de autores com paginação."""
    return await apaginate(Autor)

@router.get("/{autor_id}", response_model=Autor)
async def read_autor(autor_id: PydanticObjectId):
    """Retorna um autor pelo ID."""
    autor = await Autor.get(autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    return autor

@router.put("/{autor_id}", response_model=Autor)
async def update_autor(autor_id: PydanticObjectId, autor_data: AutorUpdate):
    """Atualiza os dados de um autor pelo ID."""
    autor = await Autor.get(autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    
    await autor.set(autor_data.model_dump(exclude_unset=True))
    return autor

@router.delete("/{autor_id}")
async def delete_autor(autor_id: PydanticObjectId):
    """Deleta um autor pelo ID."""
    autor = await Autor.get(autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    
    await autor.delete()
    return {"detail": "Autor deletado com sucesso"}


# Relacionamento com livros

@router.post("/{autor_id}/livros/{livro_id}")
async def add_livro_to_autor(autor_id: PydanticObjectId, livro_id: PydanticObjectId):
    """Vincula um livro a um autor."""
    autor = await Autor.get(autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    
    livro = await Livro.get(livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    if autor.livros is None:
        autor.livros = []
    
    for link in autor.livros:
        if link.ref.id == livro.id:
            raise HTTPException(status_code=400, detail="Livro já está vinculado a este autor")
        
    autor.livros.append(livro)
    await autor.save()
    
    if livro.autores is None:
        livro.autores = []

    ja_vinculado = any(link.ref.id == autor.id for link in livro.autores)
    if not ja_vinculado:
        livro.autores.append(autor)
        await livro.save()

    return {"detail": "Livro adicionado ao autor com sucesso"}

@router.get("/{autor_id}/livros", response_model=Page[Livro])
async def get_livros_by_autor(autor_id: PydanticObjectId):
    """Retorna os livros associados a um autor específico."""
    autor = await Autor.get(autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    query = Livro.find(Livro.autores.id == autor_id)
    
    return await apaginate(query)

@router.delete("/{autor_id}/livros/{livro_id}")
async def remove_livro_from_autor(autor_id: PydanticObjectId, livro_id: PydanticObjectId):
    """Remove o vínculo entre um livro e um autor."""
    autor = await Autor.get(autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
        
    livro = await Livro.get(livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    # Remove do autor
    if autor.livros:
        original_count = len(autor.livros)
        autor.livros = [link for link in autor.livros if link.ref.id != livro.id]
        
        if len(autor.livros) == original_count:
             raise HTTPException(status_code=404, detail="Vínculo entre livro e autor não encontrado")
             
        await autor.save()
        
    if livro.autores:
        livro.autores = [link for link in livro.autores if link.ref.id != autor.id]
        await livro.save()

    return {"detail": "Livro removido do autor com sucesso"}
