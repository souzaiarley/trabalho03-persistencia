"""
Script de seed para popular o banco de dados com dados realistas.
Cria pelo menos 10 instâncias de cada entidade.

Para executar:
    python seed.py

ou com uv:
    python -m uv run python seed.py
"""

import sys
import io
from datetime import date, timedelta
from sqlmodel import Session, select
from database import engine
from models.aluno import Aluno
from models.autor import Autor
from models.livro import Livro
from models.emprestimo import Emprestimo
from models.livro_autor_link import LivroAutorLink

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def limpar_banco():
    """Remove todos os dados existentes (opcional - use com cuidado!)"""
    print("🗑️  Limpando banco de dados...")
    with Session(engine) as session:
        # Ordem importa por causa das foreign keys
        session.query(Emprestimo).delete()
        session.query(LivroAutorLink).delete()
        session.query(Livro).delete()
        session.query(Autor).delete()
        session.query(Aluno).delete()
        session.commit()
    print("✅ Banco limpo!\n")


def seed_alunos(session: Session):
    """Cria 15 alunos realistas"""
    print("📚 Criando alunos...")

    alunos_data = [
        {"nome": "Ana Silva", "matricula": "2024001", "curso": "Ciência da Computação", "email": "ana.silva@universidade.br"},
        {"nome": "Bruno Santos", "matricula": "2024002", "curso": "Engenharia de Software", "email": "bruno.santos@universidade.br"},
        {"nome": "Carla Oliveira", "matricula": "2024003", "curso": "Sistemas de Informação", "email": "carla.oliveira@universidade.br"},
        {"nome": "Daniel Costa", "matricula": "2024004", "curso": "Ciência da Computação", "email": "daniel.costa@universidade.br"},
        {"nome": "Elena Rodrigues", "matricula": "2024005", "curso": "Engenharia de Dados", "email": "elena.rodrigues@universidade.br"},
        {"nome": "Felipe Almeida", "matricula": "2024006", "curso": "Ciência da Computação", "email": "felipe.almeida@universidade.br"},
        {"nome": "Gabriela Lima", "matricula": "2024007", "curso": "Sistemas de Informação", "email": "gabriela.lima@universidade.br"},
        {"nome": "Henrique Martins", "matricula": "2024008", "curso": "Engenharia de Software", "email": "henrique.martins@universidade.br"},
        {"nome": "Isabel Fernandes", "matricula": "2024009", "curso": "Ciência da Computação", "email": "isabel.fernandes@universidade.br"},
        {"nome": "João Pedro Souza", "matricula": "2024010", "curso": "Engenharia de Dados", "email": "joao.souza@universidade.br"},
        {"nome": "Larissa Mendes", "matricula": "2024011", "curso": "Sistemas de Informação", "email": "larissa.mendes@universidade.br"},
        {"nome": "Marcos Vieira", "matricula": "2024012", "curso": "Ciência da Computação", "email": "marcos.vieira@universidade.br"},
        {"nome": "Natália Castro", "matricula": "2024013", "curso": "Engenharia de Software", "email": "natalia.castro@universidade.br"},
        {"nome": "Otávio Ribeiro", "matricula": "2024014", "curso": "Ciência da Computação", "email": "otavio.ribeiro@universidade.br"},
        {"nome": "Paula Cardoso", "matricula": "2024015", "curso": "Engenharia de Dados", "email": "paula.cardoso@universidade.br"},
    ]

    alunos = []
    for data in alunos_data:
        aluno = Aluno(**data)
        session.add(aluno)
        alunos.append(aluno)

    session.commit()
    print(f"✅ {len(alunos)} alunos criados!\n")
    return alunos


def seed_autores(session: Session):
    """Cria 12 autores clássicos e modernos da computação"""
    print("✍️  Criando autores...")

    autores_data = [
        {"nome": "Robert C. Martin", "nacionalidade": "Estados Unidos", "ano_nascimento": 1952},
        {"nome": "Martin Fowler", "nacionalidade": "Reino Unido", "ano_nascimento": 1963},
        {"nome": "Eric Evans", "nacionalidade": "Estados Unidos", "ano_nascimento": 1960},
        {"nome": "Gang of Four (GoF)", "nacionalidade": "Internacional", "ano_nascimento": 1965},
        {"nome": "Andrew Hunt", "nacionalidade": "Estados Unidos", "ano_nascimento": 1964},
        {"nome": "David Thomas", "nacionalidade": "Estados Unidos", "ano_nascimento": 1956},
        {"nome": "Kent Beck", "nacionalidade": "Estados Unidos", "ano_nascimento": 1961},
        {"nome": "Joshua Bloch", "nacionalidade": "Estados Unidos", "ano_nascimento": 1961},
        {"nome": "Brian Kernighan", "nacionalidade": "Canadá", "ano_nascimento": 1942},
        {"nome": "Dennis Ritchie", "nacionalidade": "Estados Unidos", "ano_nascimento": 1941},
        {"nome": "Donald Knuth", "nacionalidade": "Estados Unidos", "ano_nascimento": 1938},
        {"nome": "Bjarne Stroustrup", "nacionalidade": "Dinamarca", "ano_nascimento": 1950},
    ]

    autores = []
    for data in autores_data:
        autor = Autor(**data)
        session.add(autor)
        autores.append(autor)

    session.commit()
    print(f"✅ {len(autores)} autores criados!\n")
    return autores


def seed_livros(session: Session, autores: list[Autor]):
    """Cria 15 livros clássicos de programação e engenharia de software"""
    print("📖 Criando livros...")

    livros_data = [
        {"titulo": "Clean Code", "ano": 2008, "isbn": "978-0132350884", "categoria": "Engenharia de Software"},
        {"titulo": "Refactoring", "ano": 1999, "isbn": "978-0201485677", "categoria": "Engenharia de Software"},
        {"titulo": "Domain-Driven Design", "ano": 2003, "isbn": "978-0321125217", "categoria": "Arquitetura"},
        {"titulo": "Design Patterns", "ano": 1994, "isbn": "978-0201633610", "categoria": "Padrões de Projeto"},
        {"titulo": "The Pragmatic Programmer", "ano": 1999, "isbn": "978-0201616224", "categoria": "Desenvolvimento"},
        {"titulo": "Test Driven Development", "ano": 2002, "isbn": "978-0321146533", "categoria": "Testes"},
        {"titulo": "Effective Java", "ano": 2017, "isbn": "978-0134685991", "categoria": "Java"},
        {"titulo": "The C Programming Language", "ano": 1978, "isbn": "978-0131103627", "categoria": "Linguagens"},
        {"titulo": "The Art of Computer Programming Vol 1", "ano": 1968, "isbn": "978-0201896831", "categoria": "Algoritmos"},
        {"titulo": "The C++ Programming Language", "ano": 2013, "isbn": "978-0321563842", "categoria": "Linguagens"},
        {"titulo": "Clean Architecture", "ano": 2017, "isbn": "978-0134494166", "categoria": "Arquitetura"},
        {"titulo": "Refactoring to Patterns", "ano": 2004, "isbn": "978-0321213358", "categoria": "Padrões de Projeto"},
        {"titulo": "Working Effectively with Legacy Code", "ano": 2004, "isbn": "978-0131177055", "categoria": "Manutenção"},
        {"titulo": "Introduction to Algorithms", "ano": 2009, "isbn": "978-0262033848", "categoria": "Algoritmos"},
        {"titulo": "Structure and Interpretation of Computer Programs", "ano": 1996, "isbn": "978-0262510871", "categoria": "Fundamentos"},
    ]

    livros = []
    for data in livros_data:
        livro = Livro(**data)
        session.add(livro)
        livros.append(livro)

    session.commit()
    print(f"✅ {len(livros)} livros criados!\n")
    return livros


def vincular_livros_autores(session: Session, livros: list[Livro], autores: list[Autor]):
    """Vincula livros com seus autores (relação N:N)"""
    print("🔗 Vinculando livros aos autores...")

    # Mapeamento: índice do livro -> índices dos autores
    vinculacoes = {
        0: [0],        # Clean Code -> Robert C. Martin
        1: [1],        # Refactoring -> Martin Fowler
        2: [2],        # DDD -> Eric Evans
        3: [3],        # Design Patterns -> GoF
        4: [4, 5],     # Pragmatic Programmer -> Hunt & Thomas
        5: [6],        # TDD -> Kent Beck
        6: [7],        # Effective Java -> Joshua Bloch
        7: [8, 9],     # C Language -> Kernighan & Ritchie
        8: [10],       # TAOCP -> Knuth
        9: [11],       # C++ -> Stroustrup
        10: [0],       # Clean Architecture -> Robert C. Martin
        11: [1],       # Refactoring to Patterns -> Martin Fowler
        12: [0],       # Legacy Code -> Robert C. Martin
        13: [10],      # Intro to Algorithms -> Knuth
        14: [10],      # SICP -> Knuth
    }

    for livro_idx, autores_idx in vinculacoes.items():
        livro = livros[livro_idx]
        for autor_idx in autores_idx:
            autor = autores[autor_idx]
            # Adiciona autor à lista de autores do livro
            livro.autores.append(autor)

    session.commit()
    print(f"✅ Livros vinculados aos autores!\n")


def seed_emprestimos(session: Session, alunos: list[Aluno], livros: list[Livro]):
    """Cria 20 empréstimos (ativos no prazo, finalizados e atualmente atrasados)"""
    print("📋 Criando empréstimos...")

    hoje = date.today()

    emprestimos_data = [
        {"aluno_id": alunos[0].id, "livro_id": livros[0].id, "data_emprestimo": hoje - timedelta(days=5), "data_devolucao_prevista": hoje + timedelta(days=9), "data_devolucao": None},
        {"aluno_id": alunos[1].id, "livro_id": livros[1].id, "data_emprestimo": hoje - timedelta(days=3), "data_devolucao_prevista": hoje + timedelta(days=11), "data_devolucao": None},
        {"aluno_id": alunos[2].id, "livro_id": livros[2].id, "data_emprestimo": hoje - timedelta(days=1), "data_devolucao_prevista": hoje + timedelta(days=13), "data_devolucao": None},
        {"aluno_id": alunos[3].id, "livro_id": livros[3].id, "data_emprestimo": hoje - timedelta(days=2), "data_devolucao_prevista": hoje + timedelta(days=12), "data_devolucao": None},
        
        {"aluno_id": alunos[4].id, "livro_id": livros[4].id, "data_emprestimo": hoje - timedelta(days=20), "data_devolucao_prevista": hoje - timedelta(days=5), "data_devolucao": None},
        {"aluno_id": alunos[5].id, "livro_id": livros[5].id, "data_emprestimo": hoje - timedelta(days=25), "data_devolucao_prevista": hoje - timedelta(days=10), "data_devolucao": None},
        {"aluno_id": alunos[6].id, "livro_id": livros[6].id, "data_emprestimo": hoje - timedelta(days=45), "data_devolucao_prevista": hoje - timedelta(days=30), "data_devolucao": None},

        {"aluno_id": alunos[7].id, "livro_id": livros[7].id, "data_emprestimo": hoje - timedelta(days=30), "data_devolucao_prevista": hoje - timedelta(days=16), "data_devolucao": hoje - timedelta(days=18)},
        {"aluno_id": alunos[8].id, "livro_id": livros[8].id, "data_emprestimo": hoje - timedelta(days=25), "data_devolucao_prevista": hoje - timedelta(days=11), "data_devolucao": hoje - timedelta(days=12)},
        {"aluno_id": alunos[9].id, "livro_id": livros[9].id, "data_emprestimo": hoje - timedelta(days=40), "data_devolucao_prevista": hoje - timedelta(days=26), "data_devolucao": hoje - timedelta(days=24)},
        
        {"aluno_id": alunos[10].id, "livro_id": livros[10].id, "data_emprestimo": hoje - timedelta(days=50), "data_devolucao_prevista": hoje - timedelta(days=36), "data_devolucao": hoje - timedelta(days=30)},
        {"aluno_id": alunos[11].id, "livro_id": livros[11].id, "data_emprestimo": hoje - timedelta(days=45), "data_devolucao_prevista": hoje - timedelta(days=31), "data_devolucao": hoje - timedelta(days=25)},

        {"aluno_id": alunos[12].id, "livro_id": livros[12].id, "data_emprestimo": hoje - timedelta(days=6), "data_devolucao_prevista": hoje + timedelta(days=8), "data_devolucao": None},
        {"aluno_id": alunos[13].id, "livro_id": livros[13].id, "data_emprestimo": hoje - timedelta(days=8), "data_devolucao_prevista": hoje + timedelta(days=6), "data_devolucao": None},
        {"aluno_id": alunos[14].id, "livro_id": livros[14].id, "data_emprestimo": hoje - timedelta(days=12), "data_devolucao_prevista": hoje + timedelta(days=2), "data_devolucao": None},
        {"aluno_id": alunos[0].id, "livro_id": livros[11].id, "data_emprestimo": hoje - timedelta(days=9), "data_devolucao_prevista": hoje + timedelta(days=5), "data_devolucao": None},
    ]

    emprestimos = []
    for data in emprestimos_data:
        emprestimo = Emprestimo(**data)
        session.add(emprestimo)
        emprestimos.append(emprestimo)

    session.commit()
    print(f"✅ {len(emprestimos)} empréstimos criados!")
    print(f"   - Sendo 3 atualmente atrasados (Alunos ID: {alunos[4].id}, {alunos[5].id}, {alunos[6].id})")
    return emprestimos

def exibir_estatisticas(session: Session):
    """Exibe estatísticas do banco populado"""
    print("=" * 50)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
    print("=" * 50)

    total_alunos = len(session.exec(select(Aluno)).all())
    total_autores = len(session.exec(select(Autor)).all())
    total_livros = len(session.exec(select(Livro)).all())
    total_emprestimos = len(session.exec(select(Emprestimo)).all())
    emprestimos_ativos = len(session.exec(select(Emprestimo).where(Emprestimo.data_devolucao == None)).all())

    print(f"👨‍🎓 Alunos cadastrados: {total_alunos}")
    print(f"✍️  Autores cadastrados: {total_autores}")
    print(f"📚 Livros no acervo: {total_livros}")
    print(f"📋 Total de empréstimos: {total_emprestimos}")
    print(f"🔄 Empréstimos ativos: {emprestimos_ativos}")
    print(f"✅ Empréstimos finalizados: {total_emprestimos - emprestimos_ativos}")
    print("=" * 50)


def main():
    """Função principal que executa todo o seed"""
    print("\n🌱 INICIANDO SEED DO BANCO DE DADOS\n")

    # Verificar se já existem dados no banco
    with Session(engine) as session:
        total_alunos = len(session.exec(select(Aluno)).all())
        if total_alunos > 0:
            print(f"⚠️  O banco já contém {total_alunos} alunos.")
            resposta = input("Deseja limpar o banco e começar do zero? (s/N): ")
            if resposta.lower() in ['s', 'sim', 'y', 'yes']:
                limpar_banco()
            else:
                print("❌ Seed cancelado. Banco mantido como está.")
                return

    with Session(engine) as session:
        # Criar dados na ordem correta (respeitando foreign keys)
        alunos = seed_alunos(session)
        autores = seed_autores(session)
        livros = seed_livros(session, autores)
        vincular_livros_autores(session, livros, autores)
        emprestimos = seed_emprestimos(session, alunos, livros)

        # Exibir estatísticas
        exibir_estatisticas(session)

    print("\n🎉 SEED CONCLUÍDO COM SUCESSO!\n")


if __name__ == "__main__":
    main()
