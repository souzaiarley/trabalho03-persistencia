from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from models.autor import Autor
from models.livro import Livro
from models.livro_autor_link import LivroAutorLink
from database import get_session

router = APIRouter(
    prefix="/autores",
    tags=["autores"]
)

@router.post("/", response_model=Autor)
def create_autor(autor: Autor, session: Session = Depends(get_session)):
    """Cria um novo autor."""
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor

@router.get("/", response_model=list[Autor])
def read_autores(offset: int = 0, limit: int = Query(default=10, le=100),
                 session: Session = Depends(get_session)):
    """Retorna uma lista de autores com paginação."""
    autores = session.exec(select(Autor).offset(offset).limit(limit)).all()
    return autores

@router.get("/{autor_id}", response_model=Autor)
def read_autor(autor_id: int, session: Session = Depends(get_session)):
    """Retorna um autor pelo ID."""
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    return autor

@router.put("/{autor_id}", response_model=Autor)
def update_autor(autor_id: int, autor: Autor, session: Session = Depends(get_session)):
    """Atualiza os dados de um autor pelo ID."""
    db_autor = session.get(Autor, autor_id)
    if not db_autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    for key, value in autor.model_dump(exclude_unset=True).items():
        setattr(db_autor, key, value)
    session.add(db_autor)
    session.commit()
    session.refresh(db_autor)
    return db_autor

@router.delete("/{autor_id}")
def delete_autor(autor_id: int, session: Session = Depends(get_session)):
    """Deleta um autor pelo ID."""
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    session.delete(autor)
    session.commit()
    return {"detail": "Autor deletado com sucesso"}


# Relacionamento com livros

@router.post("/{autor_id}/livros/{livro_id}")
def add_livro_to_autor(autor_id: int, livro_id: int, session: Session = Depends(get_session)):
    """Vincula um livro a um autor."""
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    
    livro = session.get(Livro, livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    existente = session.get(LivroAutorLink, (livro_id, autor_id))
    if existente:
        raise HTTPException(status_code=400, detail="Livro já está vinculado a este autor")
    
    link = LivroAutorLink(livro_id=livro_id, autor_id=autor_id)
    session.add(link)
    session.commit()
    return {"detail": "Livro adicionado ao autor com sucesso"}

@router.get("/{autor_id}/livros", response_model=list[Livro])
def get_livros_by_autor(
    autor_id: int,
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session)
):
    """Retorna os livros associados a um autor específico."""
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    statement = (
        select(Livro)
        .join(LivroAutorLink)
        .where(LivroAutorLink.autor_id == autor_id)
        .offset(offset)
        .limit(limit)
    )
    livros = session.exec(statement).all()
    return livros

@router.delete("/{autor_id}/livros/{livro_id}")
def remove_livro_from_autor(autor_id: int, livro_id: int, session: Session = Depends(get_session)):
    """Remove o vínculo entre um livro e um autor."""
    link = session.get(LivroAutorLink, (livro_id, autor_id))
    if not link:
        raise HTTPException(status_code=404, detail="Vínculo entre livro e autor não encontrado")
    session.delete(link)
    session.commit()
    return {"detail": "Livro removido do autor com sucesso"}
