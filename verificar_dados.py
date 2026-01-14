"""
Script para verificar os dados inseridos no banco de dados.
"""

import sys
import io
from sqlmodel import Session, select
from database import engine
from models.aluno import Aluno
from models.autor import Autor
from models.livro import Livro
from models.emprestimo import Emprestimo

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def main():
    with Session(engine) as session:
        print("\n" + "=" * 60)
        print("📊 VERIFICAÇÃO DOS DADOS NO BANCO")
        print("=" * 60)

        # Alunos
        print("\n👨‍🎓 ALUNOS:")
        alunos = session.exec(select(Aluno)).all()
        for aluno in alunos[:5]:  # Mostra apenas os 5 primeiros
            print(f"  • {aluno.nome} - {aluno.curso} ({aluno.matricula})")
        print(f"  ... e mais {len(alunos) - 5} alunos\n")

        # Autores
        print("✍️  AUTORES:")
        autores = session.exec(select(Autor)).all()
        for autor in autores[:5]:
            print(f"  • {autor.nome} ({autor.nacionalidade})")
        print(f"  ... e mais {len(autores) - 5} autores\n")

        # Livros com seus autores
        print("📚 LIVROS E SEUS AUTORES:")
        livros = session.exec(select(Livro)).all()
        for livro in livros[:5]:
            autores_nomes = ", ".join([a.nome for a in livro.autores])
            print(f"  • '{livro.titulo}' ({livro.ano}) - por {autores_nomes}")
            print(f"    ISBN: {livro.isbn} | Categoria: {livro.categoria}")
        print(f"  ... e mais {len(livros) - 5} livros\n")

        # Empréstimos
        print("📋 EMPRÉSTIMOS ATIVOS:")
        emprestimos_ativos = session.exec(
            select(Emprestimo).where(Emprestimo.data_devolucao == None)
        ).all()[:5]

        for emp in emprestimos_ativos:
            print(f"  • {emp.aluno.nome} pegou '{emp.livro.titulo}'")
            print(f"    Empréstimo: {emp.data_emprestimo} | Devolução prevista: {emp.data_devolucao_prevista}")

        total_ativos = len(session.exec(
            select(Emprestimo).where(Emprestimo.data_devolucao == None)
        ).all())
        print(f"  ... {total_ativos} empréstimos ativos no total\n")

        print("=" * 60)
        print("✅ Verificação concluída!")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
