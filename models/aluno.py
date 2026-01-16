from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import Optional

class AlunoCreate(BaseModel):
    nome: str
    matricula: str
    curso: str
    email: EmailStr

class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    matricula: Optional[str] = None
    curso: Optional[str] = None
    email: Optional[EmailStr] = None

class Aluno(Document):
    nome: str
    matricula: str
    curso: str
    email: EmailStr

    class Settings:
        name = "alunos"

class AlunoOut(BaseModel):
    id: str
    nome: str
    matricula: str
    curso: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }
