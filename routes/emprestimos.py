from fastapi import APIRouter, HTTPException, Query
from beanie import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import apaginate
from datetime import date
from typing import List, Optional
from models.emprestimo import Emprestimo, EmprestimoCreate, EmprestimoUpdate, EmprestimoFull
from models.aluno import Aluno, AlunoOut
from models.livro import Livro, LivroOut

router = APIRouter(
    prefix="/emprestimos",
    tags=["emprestimos"]
)

@router.post("/", response_model=Emprestimo)
async def create_emprestimo(emprestimo_data: EmprestimoCreate):
    """Cria um novo empréstimo."""
    aluno = await Aluno.get(PydanticObjectId(emprestimo_data.aluno_id))
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    livro = await Livro.get(PydanticObjectId(emprestimo_data.livro_id))
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    # Verifica se já existe um empréstimo ativo para este livro e aluno
    emprestimo_existente = await Emprestimo.find_one(
        Emprestimo.livro.id == PydanticObjectId(emprestimo_data.livro_id),
        Emprestimo.aluno.id == PydanticObjectId(emprestimo_data.aluno_id),
        Emprestimo.data_devolucao == None
    )
    if emprestimo_existente:
        raise HTTPException(status_code=400, detail="Já existe um empréstimo ativo para este livro e aluno")

    novo_emprestimo = Emprestimo(
        aluno=aluno,
        livro=livro,
        data_emprestimo=emprestimo_data.data_emprestimo,
        data_devolucao_prevista=emprestimo_data.data_devolucao_prevista,
        data_devolucao=emprestimo_data.data_devolucao
    )
    await novo_emprestimo.insert()
    return novo_emprestimo

@router.get("/", response_model=Page[EmprestimoFull])
async def read_emprestimos():
    """Retorna uma lista de todos os empréstimos."""
    return await apaginate(
        Emprestimo.find_all(),
        fetch_links=True
    )

@router.get("/{emprestimo_id}", response_model=EmprestimoFull)
async def read_emprestimo(emprestimo_id: PydanticObjectId):
    """Retorna um empréstimo pelo ID."""
    emprestimo = await Emprestimo.get(emprestimo_id, fetch_links=True)
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    
    return EmprestimoFull(
        id=str(emprestimo.id),
        data_emprestimo=emprestimo.data_emprestimo,
        data_devolucao_prevista=emprestimo.data_devolucao_prevista,
        data_devolucao=emprestimo.data_devolucao,
        aluno=AlunoOut(
            id=str(emprestimo.aluno.id),
            nome=emprestimo.aluno.nome,
            matricula=emprestimo.aluno.matricula,
            curso=emprestimo.aluno.curso,
            email=emprestimo.aluno.email
        ),
        livro=LivroOut(
            id=str(emprestimo.livro.id),
            titulo=emprestimo.livro.titulo,
            ano=emprestimo.livro.ano,
            isbn=emprestimo.livro.isbn,
            categoria=emprestimo.livro.categoria
        )
    )

@router.put("/{emprestimo_id}", response_model=Emprestimo)
async def update_emprestimo(emprestimo_id: PydanticObjectId, emprestimo_data: EmprestimoUpdate):
    """Atualiza os dados de um empréstimo pelo ID."""
    db_emprestimo = await Emprestimo.get(emprestimo_id, fetch_links=True)
    if not db_emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    
    update_dict = emprestimo_data.model_dump(exclude_unset=True)
    
    if 'aluno_id' in update_dict:
        aluno = await Aluno.get(PydanticObjectId(update_dict['aluno_id']))
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        db_emprestimo.aluno = aluno
        del update_dict['aluno_id']
        
    if 'livro_id' in update_dict:
        livro = await Livro.get(PydanticObjectId(update_dict['livro_id']))
        if not livro:
            raise HTTPException(status_code=404, detail="Livro não encontrado")
        db_emprestimo.livro = livro
        del update_dict['livro_id']
    
    # Verifica se já existe um empréstimo ativo para este livro e aluno (se mudou um deles)
    aluno_id_check = db_emprestimo.aluno.id
    livro_id_check = db_emprestimo.livro.id
    
    emprestimo_ativo = await Emprestimo.find_one(
        Emprestimo.aluno.id == aluno_id_check,
        Emprestimo.livro.id == livro_id_check,
        Emprestimo.data_devolucao == None,
        Emprestimo.id != emprestimo_id
    )
    if emprestimo_ativo:
        raise HTTPException(status_code=400, detail="Já existe um empréstimo ativo para este livro e aluno")
    
    # Atualiza campos restantes (datas)
    if update_dict:
        await db_emprestimo.set(update_dict)
    else:
        await db_emprestimo.save()
        
    return db_emprestimo

@router.delete("/{emprestimo_id}")
async def delete_emprestimo(emprestimo_id: PydanticObjectId):
    """Deleta um empréstimo pelo ID."""
    emprestimo = await Emprestimo.get(emprestimo_id)
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    
    await emprestimo.delete()
    return {"detail": "Empréstimo deletado com sucesso"}


# Consultas complexas

@router.get("/atrasados/listar", response_model=Page[EmprestimoFull])
async def get_emprestimos_atrasados():
    """Retorna todos os empréstimos atrasados (data_devolucao_prevista < hoje e ainda não devolvidos)."""
    hoje = date.today()
    query = Emprestimo.find(
        Emprestimo.data_devolucao == None,
        Emprestimo.data_devolucao_prevista < hoje
    ).fetch_links()

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


@router.get("/ativos/listar", response_model=Page[EmprestimoFull])
async def get_emprestimos_ativos():
    """Retorna todos os empréstimos ativos (ainda não devolvidos)."""
    query = Emprestimo.find(Emprestimo.data_devolucao == None).fetch_links()

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
