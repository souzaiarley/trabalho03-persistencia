from sqlmodel import SQLModel, Field

class LivroAutorLink(SQLModel, table=True):
    """Tabela de ligação N:N entre livros e autores"""
    livro_id: int = Field(foreign_key='livro.id', primary_key=True)
    autor_id: int = Field(foreign_key='autor.id', primary_key=True)