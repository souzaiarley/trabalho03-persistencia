import sys
import io
import os
import asyncio
from datetime import date, timedelta
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from models.aluno import Aluno
from models.autor import Autor
from models.livro import Livro
from models.emprestimo import Emprestimo

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
MONGO_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")


async def init_db():
    client = AsyncIOMotorClient(MONGO_URL)
    await init_beanie(
        database=client.biblioteca,
        document_models=[Aluno, Autor, Livro, Emprestimo],
    )


async def limpar_banco():
    print("🗑️  Limpando banco de dados...")
    await Emprestimo.delete_all()
    await Livro.delete_all()
    await Autor.delete_all()
    await Aluno.delete_all()
    print("✅ Banco limpo!\n")


async def seed_alunos():
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
        await aluno.insert()
        alunos.append(aluno)

    print(f"✅ {len(alunos)} alunos criados!\n")
    return alunos


async def seed_autores():
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
        await autor.insert()
        autores.append(autor)

    print(f"✅ {len(autores)} autores criados!\n")
    return autores


async def seed_livros(autores):
    print("📖 Criando livros...")

    livros_data = [
        {"titulo": "Clean Code", "ano": 2008, "isbn": "978-0132350884", "categoria": "Engenharia de Software", "autores": [autores[0]]},
        {"titulo": "Refactoring", "ano": 1999, "isbn": "978-0201485677", "categoria": "Engenharia de Software", "autores": [autores[1]]},
        {"titulo": "Domain-Driven Design", "ano": 2003, "isbn": "978-0321125217", "categoria": "Arquitetura", "autores": [autores[2]]},
        {"titulo": "Design Patterns", "ano": 1994, "isbn": "978-0201633610", "categoria": "Padrões de Projeto", "autores": [autores[3]]},
        {"titulo": "The Pragmatic Programmer", "ano": 1999, "isbn": "978-0201616224", "categoria": "Desenvolvimento", "autores": [autores[4], autores[5]]},
        {"titulo": "Test Driven Development", "ano": 2002, "isbn": "978-0321146533", "categoria": "Testes", "autores": [autores[6]]},
        {"titulo": "Effective Java", "ano": 2017, "isbn": "978-0134685991", "categoria": "Java", "autores": [autores[7]]},
        {"titulo": "The C Programming Language", "ano": 1978, "isbn": "978-0131103627", "categoria": "Linguagens", "autores": [autores[8], autores[9]]},
        {"titulo": "The Art of Computer Programming Vol 1", "ano": 1968, "isbn": "978-0201896831", "categoria": "Algoritmos", "autores": [autores[10]]},
        {"titulo": "The C++ Programming Language", "ano": 2013, "isbn": "978-0321563842", "categoria": "Linguagens", "autores": [autores[11]]},
        {"titulo": "Clean Architecture", "ano": 2017, "isbn": "978-0134494166", "categoria": "Arquitetura", "autores": [autores[0]]},
        {"titulo": "Refactoring to Patterns", "ano": 2004, "isbn": "978-0321213358", "categoria": "Padrões de Projeto", "autores": [autores[1]]},
        {"titulo": "Working Effectively with Legacy Code", "ano": 2004, "isbn": "978-0131177055", "categoria": "Manutenção", "autores": [autores[0]]},
        {"titulo": "Introduction to Algorithms", "ano": 2009, "isbn": "978-0262033848", "categoria": "Algoritmos", "autores": [autores[10]]},
        {"titulo": "Structure and Interpretation of Computer Programs", "ano": 1996, "isbn": "978-0262510871", "categoria": "Fundamentos", "autores": [autores[10]]},
    ]

    livros = []
    for data in livros_data:
        livro = Livro(**data)
        await livro.insert()
        livros.append(livro)

    print(f"✅ {len(livros)} livros criados!\n")
    return livros


async def seed_emprestimos(alunos, livros):
    print("📋 Criando empréstimos...")

    hoje = date.today()

    emprestimos_data = [
        {"aluno": alunos[0], "livro": livros[0], "data_emprestimo": hoje - timedelta(days=5), "data_devolucao_prevista": hoje + timedelta(days=9)},
        {"aluno": alunos[1], "livro": livros[1], "data_emprestimo": hoje - timedelta(days=3), "data_devolucao_prevista": hoje + timedelta(days=11)},
        {"aluno": alunos[2], "livro": livros[2], "data_emprestimo": hoje - timedelta(days=1), "data_devolucao_prevista": hoje + timedelta(days=13)},
        {"aluno": alunos[3], "livro": livros[3], "data_emprestimo": hoje - timedelta(days=2), "data_devolucao_prevista": hoje + timedelta(days=12)},
        {"aluno": alunos[4], "livro": livros[4], "data_emprestimo": hoje - timedelta(days=20), "data_devolucao_prevista": hoje - timedelta(days=5), "data_devolucao": hoje - timedelta(days=3)},
        {"aluno": alunos[5], "livro": livros[5], "data_emprestimo": hoje - timedelta(days=15), "data_devolucao_prevista": hoje - timedelta(days=2), "data_devolucao": None},
        {"aluno": alunos[6], "livro": livros[6], "data_emprestimo": hoje - timedelta(days=45), "data_devolucao_prevista": hoje - timedelta(days=30), "data_devolucao": hoje - timedelta(days=28)},
        {"aluno": alunos[7], "livro": livros[7], "data_emprestimo": hoje - timedelta(days=30), "data_devolucao_prevista": hoje - timedelta(days=16), "data_devolucao": hoje - timedelta(days=18)},
        {"aluno": alunos[8], "livro": livros[8], "data_emprestimo": hoje - timedelta(days=25), "data_devolucao_prevista": hoje - timedelta(days=11), "data_devolucao": hoje - timedelta(days=12)},
        {"aluno": alunos[9], "livro": livros[9], "data_emprestimo": hoje - timedelta(days=40), "data_devolucao_prevista": hoje - timedelta(days=26), "data_devolucao": hoje - timedelta(days=24)},
        {"aluno": alunos[10], "livro": livros[10], "data_emprestimo": hoje - timedelta(days=50), "data_devolucao_prevista": hoje - timedelta(days=36), "data_devolucao": hoje - timedelta(days=30)},
        {"aluno": alunos[11], "livro": livros[11], "data_emprestimo": hoje - timedelta(days=45), "data_devolucao_prevista": hoje - timedelta(days=31), "data_devolucao": hoje - timedelta(days=25)},
        {"aluno": alunos[12], "livro": livros[12], "data_emprestimo": hoje - timedelta(days=6), "data_devolucao_prevista": hoje + timedelta(days=8)},
        {"aluno": alunos[13], "livro": livros[13], "data_emprestimo": hoje - timedelta(days=8), "data_devolucao_prevista": hoje + timedelta(days=6)},
        {"aluno": alunos[14], "livro": livros[14], "data_emprestimo": hoje - timedelta(days=12), "data_devolucao_prevista": hoje + timedelta(days=2)},
        {"aluno": alunos[0], "livro": livros[11], "data_emprestimo": hoje - timedelta(days=9), "data_devolucao_prevista": hoje + timedelta(days=5)},
        {"aluno": alunos[1], "livro": livros[10], "data_emprestimo": hoje - timedelta(days=7), "data_devolucao_prevista": hoje + timedelta(days=7)},
        {"aluno": alunos[2], "livro": livros[9], "data_emprestimo": hoje - timedelta(days=15), "data_devolucao_prevista": hoje + timedelta(days=1)},
        {"aluno": alunos[3], "livro": livros[8], "data_emprestimo": hoje - timedelta(days=18), "data_devolucao_prevista": hoje - timedelta(days=2), "data_devolucao": hoje - timedelta(days=1)},
        {"aluno": alunos[4], "livro": livros[7], "data_emprestimo": hoje - timedelta(days=20), "data_devolucao_prevista": hoje - timedelta(days=5), "data_devolucao": hoje - timedelta(days=4)},
    ]

    emprestimos = []
    for data in emprestimos_data:
        emprestimo = Emprestimo(**data)
        await emprestimo.insert()
        emprestimos.append(emprestimo)

    print(f"✅ {len(emprestimos)} empréstimos criados!\n")
    return emprestimos


async def main():
    print("\n🌱 INICIANDO SEED DO BANCO DE DADOS\n")
    await init_db()

    total_alunos = await Aluno.count()
    if total_alunos > 0:
        print(f"⚠️  O banco já contém {total_alunos} alunos.")
        resposta = input("Deseja limpar o banco e começar do zero? (s/N): ")
        if resposta.lower() in ['s', 'sim', 'y', 'yes']:
            await limpar_banco()
        else:
            print("❌ Seed cancelado. Banco mantido como está.")
            return

    alunos = await seed_alunos()
    autores = await seed_autores()
    livros = await seed_livros(autores)
    await seed_emprestimos(alunos, livros)

    # Exibir estatísticas
    print("=" * 50)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
    print("=" * 50)
    print(f"👨‍🎓 Alunos cadastrados: {await Aluno.count()}")
    print(f"✍️  Autores cadastrados: {await Autor.count()}")
    print(f"📚 Livros no acervo: {await Livro.count()}")
    print(f"📋 Total de empréstimos: {await Emprestimo.count()}")
    emprestimos_ativos = await Emprestimo.find({"data_devolucao": None}).to_list()
    print(f"🔄 Empréstimos ativos: {len(emprestimos_ativos)}")
    print(f"✅ Empréstimos finalizados: {await Emprestimo.count() - len(emprestimos_ativos)}")
    print("=" * 50)

    print("\n🎉 SEED CONCLUÍDO COM SUCESSO!\n")


if __name__ == "__main__":
    asyncio.run(main())
