from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from datetime import date
from models.emprestimo import Emprestimo, EmprestimoInput, EmprestimoFull
from models.aluno import Aluno
from models.livro import Livro
from database import get_session

router = APIRouter(
    prefix="/emprestimos",
    tags=["emprestimos"]
)

@router.post("/", response_model=Emprestimo)
def create_emprestimo(emprestimo: EmprestimoInput, session: Session = Depends(get_session)):
    """Cria um novo empréstimo."""
    aluno = session.get(Aluno, emprestimo.aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    livro = session.get(Livro, emprestimo.livro_id)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    emprestimo_existente = session.exec(
        select(Emprestimo).where(
            (Emprestimo.livro_id == emprestimo.livro_id) &
            (Emprestimo.aluno_id == emprestimo.aluno_id) &
            (Emprestimo.data_devolucao == None)
        )
    ).first()
    if emprestimo_existente:
        raise HTTPException(status_code=400, detail="Já existe um empréstimo ativo para este livro e aluno")

    novo_emprestimo = Emprestimo(
        aluno_id=emprestimo.aluno_id,
        livro_id=emprestimo.livro_id,
        data_emprestimo=emprestimo.data_emprestimo,
        data_devolucao_prevista=emprestimo.data_devolucao_prevista,
        data_devolucao=emprestimo.data_devolucao
    )
    session.add(novo_emprestimo)
    session.commit()
    session.refresh(novo_emprestimo)
    return novo_emprestimo

@router.get("/", response_model=list[EmprestimoFull])
def read_emprestimos(offset: int = 0, limit: int = Query(default=10, le=100),
                     session: Session = Depends(get_session)):
    """Retorna uma lista de todos os empréstimos."""
    statement = (
        select(Emprestimo)
        .options(
            selectinload(Emprestimo.aluno),
            selectinload(Emprestimo.livro)
        )
        .offset(offset)
        .limit(limit)
    )
    emprestimos = session.exec(statement).all()
    return emprestimos

@router.get("/{emprestimo_id}", response_model=EmprestimoFull)
def read_emprestimo(emprestimo_id: int, session: Session = Depends(get_session)):
    """Retorna um empréstimo pelo ID."""
    statement = (
        select(Emprestimo)
        .where(Emprestimo.id == emprestimo_id)
        .options(
            selectinload(Emprestimo.aluno),
            selectinload(Emprestimo.livro)
        )
    )
    emprestimo = session.exec(statement).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    return emprestimo

@router.put("/{emprestimo_id}", response_model=Emprestimo)
def update_emprestimo(emprestimo_id: int, emprestimo: EmprestimoInput,
                      session: Session = Depends(get_session)):
    """Atualiza os dados de um empréstimo pelo ID."""
    db_emprestimo = session.get(Emprestimo, emprestimo_id)
    if not db_emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    
    data = emprestimo.model_dump(exclude_unset=True)
    if 'aluno_id' in data:
        aluno = session.get(Aluno, data['aluno_id'])
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
    if 'livro_id' in data:
        livro = session.get(Livro, data['livro_id'])
        if not livro:
            raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    aluno_id_check = data.get('aluno_id', db_emprestimo.aluno_id)
    livro_id_check = data.get('livro_id', db_emprestimo.livro_id)
    
    emprestimo_ativo = session.exec(
        select(Emprestimo)
        .where(
            (Emprestimo.aluno_id == aluno_id_check) &
            (Emprestimo.livro_id == livro_id_check) &
            (Emprestimo.data_devolucao == None) &
            (Emprestimo.id != emprestimo_id)
        )
    ).first()
    if emprestimo_ativo:
        raise HTTPException(status_code=400, detail="Já existe um empréstimo ativo para este livro e aluno")
    
    for key, value in data.items():
        setattr(db_emprestimo, key, value)
    session.add(db_emprestimo)
    session.commit()
    session.refresh(db_emprestimo)
    return db_emprestimo

@router.delete("/{emprestimo_id}")
def delete_emprestimo(emprestimo_id: int, session: Session = Depends(get_session)):
    """Deleta um empréstimo pelo ID."""
    emprestimo = session.get(Emprestimo, emprestimo_id)
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    session.delete(emprestimo)
    session.commit()
    return {"detail": "Empréstimo deletado com sucesso"}


# Consultas complexas

@router.get("/atrasados/listar", response_model=list[EmprestimoFull])
def get_emprestimos_atrasados(
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session)
):
    """Retorna todos os empréstimos atrasados (data_devolucao_prevista < hoje e ainda não devolvidos)."""
    hoje = date.today()
    statement = (
        select(Emprestimo)
        .where(
            (Emprestimo.data_devolucao == None) &
            (Emprestimo.data_devolucao_prevista < hoje)
        )
        .offset(offset)
        .limit(limit)
        .options(
            selectinload(Emprestimo.aluno),
            selectinload(Emprestimo.livro)
        )
    )
    emprestimos = session.exec(statement).all()
    return emprestimos


@router.get("/ativos/listar", response_model=list[EmprestimoFull])
def get_emprestimos_ativos(
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session)
):
    """Retorna todos os empréstimos ativos (ainda não devolvidos)."""
    statement = (
        select(Emprestimo)
        .where(Emprestimo.data_devolucao == None)
        .offset(offset)
        .limit(limit)
        .options(
            selectinload(Emprestimo.aluno),
            selectinload(Emprestimo.livro)
        )
    )
    emprestimos = session.exec(statement).all()
    return emprestimos
