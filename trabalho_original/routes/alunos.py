from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from models.aluno import Aluno
from models.emprestimo import Emprestimo, EmprestimoWithLivro
from database import get_session

router = APIRouter(
    prefix="/alunos",
    tags=["alunos"]
)

@router.post("/", response_model=Aluno)
def create_aluno(aluno: Aluno, session: Session = Depends(get_session)):
    """Cria um novo aluno."""
    session.add(aluno)
    session.commit()
    session.refresh(aluno)
    return aluno

@router.get("/", response_model=list[Aluno])
def read_alunos(offset: int = 0, limit: int = Query(default=10, le=100),
                session: Session = Depends(get_session)):
    """Retorna uma lista de alunos com paginação."""
    alunos = session.exec(select(Aluno).offset(offset).limit(limit)).all()
    return alunos

@router.get("/{aluno_id}", response_model=Aluno)
def read_aluno(aluno_id: int, session: Session = Depends(get_session)):
    """Retorna um aluno pelo ID."""
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno

@router.put("/{aluno_id}", response_model=Aluno)
def update_aluno(aluno_id: int, aluno: Aluno, session: Session = Depends(get_session)):
    """Atualiza os dados de um aluno pelo ID."""
    db_aluno = session.get(Aluno, aluno_id)
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    for key, value in aluno.model_dump(exclude_unset=True).items():
        setattr(db_aluno, key, value)
    session.add(db_aluno)
    session.commit()
    session.refresh(db_aluno)
    return db_aluno

@router.delete("/{aluno_id}")
def delete_aluno(aluno_id: int, session: Session = Depends(get_session)):
    """Deleta um aluno pelo ID."""
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    session.delete(aluno)
    session.commit()
    return {"detail": "Aluno deletado com sucesso"}


# Relacionamento com emprestimos

@router.get("/{aluno_id}/emprestimos", response_model=list[EmprestimoWithLivro])
def get_emprestimos_of_aluno(
    aluno_id: int,
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session)
):  
    """Retorna os empréstimos de um aluno específico com paginação."""
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    statement = (
        select(Emprestimo)
        .where(Emprestimo.aluno_id == aluno_id)
        .offset(offset)
        .limit(limit)
        .options(selectinload(Emprestimo.livro))
    )
    emprestimos = session.exec(statement).all()
    return emprestimos