<p align="center">
  <img src="docs/images/logo.png" alt="Doutor Ludo Logo" width="200"/>
</p>

# 🎲 Doutor Ludo

O **Doutor Ludo** é uma plataforma web de aluguel de jogos de tabuleiro que facilita o acesso a um catálogo variado de jogos, proporcionando comodidade com entrega e coleta porta-a-porta. O sistema combina a locação com a base de conhecimento *WikiLudo* e um sistema de reservas.

O objetivo principal deste repositório é o desenvolvimento e a validação do Produto Mínimo Viável (MVP) do sistema, consolidando as práticas de Engenharia de Software. O foco da implementação está em viabilizar o fluxo central de negócios da plataforma.

---

## 🎓 Informações Acadêmicas

| Contexto | Detalhes |
| :--- | :--- |
| **Curso** | Ciência da Computação (7º Semestre) |
| **Disciplina** | Engenharia de Software II |
| **Período** | 1º Semestre de 2026 |
| **Professor / Orientador** | Diego Roberto Gonçalves de Pontes |

### 👥 Integrantes do Grupo

* Gabriel Henrique Custodio
* João Eduardo Lino Quinteiro
* Jules Eloísio Moraes Lima
* Kleberson Crystyan de Lima
* Vitor Hugo Granato Moreira do Prado

---

## 💻 Tecnologias Utilizadas

Para a construção e execução do MVP, planeja-se a utilização das seguintes tecnologias:

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white&labelColor=black)

![CSS3](https://img.shields.io/badge/CSS3-663399?style=for-the-badge&logo=css&logoColor=white&labelColor=black)

![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=white&labelColor=black)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=black)

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=black)

![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white&labelColor=black)

---

## 📁 Estrutura do Projeto

```
│   .gitignore
│   README.md
│
├───docs
│   ├───images
│   │       chess.jpg
│   │       diagrama_de_classes.png
│   │       logo.png
│   │
│   ├───sprint_00_warmup
│   │       warmup.md
│   │
│   ├───sprint_01-02
│   │       requisitos_e_classes.md
│   │
│   ├───sprint_03
│   │       arquitetura.md
│   │
│   └───sprint_04
│           integracao_planejamento_mvp.md
│
└───src
    ├───backend
    │   │   main.py
    │   │   requirements.txt
    │   │
    │   ├───adapters
    │   │   │   __init__.py
    │   │   │
    │   │   ├───inbound
    │   │   │       http_controller.py
    │   │   │       __init__.py
    │   │   │
    │   │   └───outbound
    │   │           memory_repository.py
    │   │           mock_adapters.py
    │   │           __init__.py
    │   │
    │   ├───domain
    │   │       entities.py
    │   │       services.py
    │   │       __init__.py
    │   │
    │   └───ports
    │           outputs.py
    │           __init__.py
    │
    └───frontend
        │   app.js
        │   index.html
        │   style.css
        │
        └───assets
                logo.png
```

---

## 📖 Instruções de uso

> As instruções de instalação, execução e configuração serão adicionadas após a criação do MVP.

---

## Documentação

<ol>
<li><a href="docs/sprint_00_warmup/warmup.md"> Warmup</a></li>
<li><a href="docs/sprint_01-02/requisitos_e_classes.md"> Sprint 1 - Análise dos Requisitos e Identificação das Classes</a></li>
<li><a href="docs/sprint_01-02/requisitos_e_classes.md"> Sprint 2 - Modelagem de Classes e Relacionamentos</a></li>
<li><a href="docs/sprint_03/arquitetura.md"> Sprint 3 - Definição da Arquitetura do Sistema</a></li>
<li><a href="docs/sprint_04/integracao_planejamento_mvp.md"> Sprint 4 - Organização, Integração e Planejamento do MVP</a></li>
</ol>

---

## 💻 Código

A pasta `src/` concentrará os arquivos de implementação do MVP.

---

<p align="center">
  <sub>&copy; 2026 Doutor Ludo. Desenvolvido para a disciplina de Engenharia de Software II — PUC Minas.</sub>
</p>
