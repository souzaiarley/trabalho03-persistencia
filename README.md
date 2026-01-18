# Diagrama de Classes - Sistema de Biblioteca

```mermaid
classDiagram

    class Emprestimo {
        +date data_emprestimo
        +date data_devolucao_prevista
        +date data_devolucao
    }
    
    class Livro {
        +string titulo
        +int ano
        +string isbn
        +string categoria
    }

    class Autor {
        +string nome
        +string nacionalidade
        +int ano_nascimento
    }

    class Aluno {
        +string nome
        +string matricula
        +string curso
        +string email
    }

    %% Relacionamentos
    
    %% 1 Livro pode ter vários registros de empréstimo
    Livro "1" --> "*" Emprestimo
    
    %% 1 Aluno pode realizar vários empréstimos
    Aluno "1" --> "*" Emprestimo
    
    %% Relacionamento Muitos-para-Muitos (Conceitual)
    Livro "*" -- "*" Autor 
```
