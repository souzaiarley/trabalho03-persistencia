from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, func, or_
from sqlalchemy.orm import selectinload
from models.livro import Livro, LivroComEstatisticas
from models.livro_autor_link import LivroAutorLink
from models.autor import Autor
from models.emprestimo import Emprestimo, EmprestimoWithAluno
from database import get_session

router = APIRouter(
    prefix="/livros",
    tags=["livros"]
)

@router.post("/", response_model=Livro)
def create_livro(livro: Livro, session: Session = Depends(get_session)):
    """Cria um novo livro."""
    session.add(livro)
    session.commit()
    session.refresh(livro)
    return livro

@router.get("/", response_model=list[Livro])
def read_livros(offset: int = 0, limit: int = Query(default=10, le=100),
                session: Session = Depends(get_session)):
    """Retorna uma lista de livros com paginação."""
    livros = session.exec(select(Livro).offset(offset).limit(limit)).all()
    return livros

@router.get("/{livro_id}", response_model=Livro)
def read_livro(livro_id: int, session: Session = Depends(get_session)):
    """Retorna um livro pelo ID."""
    livro = session.get(Livro, livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro

@router.put("/{livro_id}", response_model=Livro)
def update_livro(livro_id: int, livro: Livro, session: Session = Depends(get_session)):
    """Atualiza os dados de um livro pelo ID."""
    db_livro = session.get(Livro, livro_id)
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    for key, value in livro.model_dump(exclude_unset=True).items():
        setattr(db_livro, key, value)
    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)
    return db_livro

@router.delete("/{livro_id}")
def delete_livro(livro_id: int, session: Session = Depends(get_session)):
    """Deleta um livro pelo ID."""
    livro = session.get(Livro, livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    session.delete(livro)
    session.commit()
    return {"detail": "Livro deletado com sucesso"}


# Relacionamento com autores

@router.post("/{livro_id}/autores/{autor_id}")
def add_autor_to_livro(livro_id: int, autor_id: int, session: Session = Depends(get_session)):
    """Vincula um autor a um livro."""
    livro = session.get(Livro, livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    existente = session.get(LivroAutorLink, (livro_id, autor_id))
    if existente:
        raise HTTPException(status_code=400, detail="Autor já está vinculado a este livro")

    link = LivroAutorLink(livro_id=livro_id, autor_id=autor_id)
    session.add(link)
    session.commit()
    return {"detail": "Autor adicionado ao livro com sucesso"}

@router.get("/{livro_id}/autores", response_model=list[Autor])
def get_autores_of_livro(
    livro_id: int,
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session)
):
    """Retorna os autores associados a um livro."""
    livro = session.get(Livro, livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    statement = (
        select(Autor)
        .join(LivroAutorLink)
        .where(LivroAutorLink.livro_id == livro_id)
        .offset(offset)
        .limit(limit)
    )
    autores = session.exec(statement).all()
    return autores

@router.delete("/{livro_id}/autores/{autor_id}")
def remove_autor_from_livro(livro_id: int, autor_id: int, session: Session = Depends(get_session)):
    """Remove o vínculo de um autor com um livro."""
    link = session.get(LivroAutorLink, (livro_id, autor_id))
    if not link:
        raise HTTPException(status_code=404, detail="Vínculo entre livro e autor não encontrado")
    session.delete(link)
    session.commit()
    return {"detail": "Autor removido do livro com sucesso"}


# Relacionamento com emprestimos

@router.get("/{livro_id}/emprestimos", response_model=list[EmprestimoWithAluno])
def get_emprestimos_of_livro(
    livro_id: int,
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session)
):  
    """Retorna os empréstimos de um livro."""
    livro = session.get(Livro, livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    statement = (
        select(Emprestimo)
        .where(Emprestimo.livro_id == livro_id)
        .offset(offset)
        .limit(limit)
        .options(selectinload(Emprestimo.aluno))
    )
    emprestimos = session.exec(statement).all()
    return emprestimos


# Consultas complexas

@router.get("/buscar/query", response_model=list[Livro])
def buscar_livros(
    q: str = Query(..., description="Termo de busca (título, categoria ou autor)"),
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session)
):
    """Busca livros por título, categoria ou nome do autor."""
    # Busca por título ou categoria
    statement = (
        select(Livro)
        .where(
            or_(
                Livro.titulo.ilike(f"%{q}%"),
                Livro.categoria.ilike(f"%{q}%")
            )
        )
    )
    livros_titulo_categoria = session.exec(statement).all()

    # Busca por autor
    statement_autor = (
        select(Livro)
        .join(LivroAutorLink)
        .join(Autor)
        .where(Autor.nome.ilike(f"%{q}%"))
    )
    livros_autor = session.exec(statement_autor).all()

    # Combinar resultados e remover duplicatas mantendo ordem
    livros_dict = {
        livro.id: livro
        for livro in livros_titulo_categoria + livros_autor
    }
    livros = list(livros_dict.values())
    return livros[offset : offset + limit]


@router.get("/mais-emprestados/ranking", response_model=list[LivroComEstatisticas])
def get_livros_mais_emprestados(
    limit: int = Query(default=10, le=50, description="Número de livros a retornar"),
    session: Session = Depends(get_session)
):
    """
    Retorna os livros mais emprestados com estatísticas.
    """
    # Query para contar empréstimos por livro
    statement = (
        select(
            Livro,
            func.count(Emprestimo.id).label('total_emprestimos'),
            func.count(
                func.nullif(Emprestimo.data_devolucao, Emprestimo.data_devolucao)
            ).label('emprestimos_ativos')
        )
        .outerjoin(Emprestimo, Livro.id == Emprestimo.livro_id)
        .group_by(Livro.id)
        .order_by(func.count(Emprestimo.id).desc())
        .limit(limit)
    )

    results = session.exec(statement).all()

    # Construir resposta com estatísticas
    livros_com_stats = []
    for livro, total, ativos in results:
        # Contar empréstimos ativos manualmente (mais confiável)
        ativos_count = session.exec(
            select(func.count(Emprestimo.id))
            .where(
                (Emprestimo.livro_id == livro.id) &
                (Emprestimo.data_devolucao == None)
            )
        ).first()

        livro_dict = livro.model_dump()
        livro_dict['total_emprestimos'] = total or 0
        livro_dict['emprestimos_ativos'] = ativos_count or 0
        livros_com_stats.append(LivroComEstatisticas(**livro_dict))

    return livros_com_stats


@router.get("/por-categoria/filtrar", response_model=list[Livro])
def get_livros_por_categoria(
    categoria: str = Query(..., description="Nome da categoria"),
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session)
):
    """Filtra livros por categoria."""
    statement = (
        select(Livro)
        .where(Livro.categoria.ilike(f"%{categoria}%"))
        .offset(offset)
        .limit(limit)
    )
    livros = session.exec(statement).all()
    return livros