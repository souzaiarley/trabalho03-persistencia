from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from models import Aluno, AlunoCreate, AlunoUpdate, Emprestimo

router = APIRouter(
    prefix="/alunos",
    tags=["alunos"]
)

@router.post("/", response_model=Aluno)
async def create_aluno(aluno: AlunoCreate):
    await aluno.insert()
    return aluno

@router.get("/", response_model=Page[Aluno])
async def read_alunos():
    return await apaginate(Aluno)

@router.get("/{aluno_id}", response_model=Aluno)
async def read_aluno(aluno_id: PydanticObjectId):
    aluno = await Aluno.get(aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno

@router.put("/{aluno_id}", response_model=Aluno)
async def update_aluno(aluno_id: PydanticObjectId, aluno_data: AlunoUpdate):
    aluno = await Aluno.get(aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    await aluno.set(aluno_data.model_dump(exclude_unset=True))
    return aluno

@router.delete("/{aluno_id}")
async def delete_aluno(aluno_id: PydanticObjectId):
    aluno = await Aluno.get(aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    await aluno.delete()
    return {"detail": "Aluno deletado com sucesso"}


# Relacionamento com emprestimos

@router.get("/{aluno_id}/emprestimos", response_model=list[Emprestimo])
async def get_emprestimos_aluno(aluno_id: PydanticObjectId):
    aluno = await Aluno.get(aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    return await apaginate(
        Emprestimo.find(
            Emprestimo.aluno.id == aluno_id
        ).fetch_links()
    )
