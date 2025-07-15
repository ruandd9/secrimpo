# SECRIMPO

Sistema para registro de ocorrências, itens apreendidos e geração automática de planilhas Excel, termo de apreensão e etiquetas, voltado para agentes SECRIMPO.

## Visão Geral
O SECRIMPO é um sistema local, simples e eficiente, desenvolvido em Python, que permite:
- Cadastro de ocorrências policiais
- Registro de policiais, proprietários e itens apreendidos
- Exportação automática de dados para planilhas Excel
- Geração de termo de apreensão e etiquetas

## Tecnologias Utilizadas
- **Python 3.x**
- **SQLite** (banco de dados local)
- **SQLAlchemy** (ORM)
- **Pandas** (manipulação/exportação de dados)
- **Tkinter** (interface gráfica)

## Estrutura de Diretórios
```
secrimpo/
│
├── main.py                # Ponto de entrada do sistema (Tkinter)
├── models/                # Modelos SQLAlchemy
│   ├── __init__.py
│   ├── ocorrencia.py
│   ├── policial.py
│   ├── item_apreendido.py
│   └── proprietario.py
├── database/              # Inicialização e conexão com SQLite
│   └── db.py
├── ui/                    # Telas e formulários Tkinter
│   ├── __init__.py
│   ├── tela_ocorrencia.py
│   ├── tela_policial.py
│   ├── tela_item.py
│   └── tela_proprietario.py
├── export/                # Exportação para Excel e geração de documentos
│   ├── __init__.py
│   ├── excel_export.py
│   └── termo_etiqueta.py
└── utils/                 # Funções utilitárias
    └── helpers.py
```

## Instalação
1. **Clone o repositório:**
   ```bash
   git clone 
   cd secrimpo
   ```
2. **(Opcional) Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```
3. **Instale as dependências:**
   ```bash
   pip install sqlalchemy pandas openpyxl
   ```

## Como Executar
1. Execute o sistema:
   ```bash
   python main.py
   ```
2. Siga as instruções na interface gráfica para cadastrar ocorrências, policiais, itens e proprietários.

## Funcionalidades
- Cadastro completo de ocorrências
- Cadastro de policiais e proprietários
- Registro de múltiplos itens apreendidos por ocorrência
- Associação de itens a proprietários e policiais
- Exportação automática para Excel (mensal/anual)
- Geração de termo de apreensão e etiquetas

## Requisitos Funcionais e Não Funcionais
- Operação local, sem necessidade de internet
- Interface simples e objetiva
- Código modular e de fácil manutenção

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença
Este projeto é livre para uso acadêmico e institucional. Consulte o arquivo LICENSE para mais detalhes.

---
Desenvolvido para facilitar o trabalho dos agentes SECRIMPO no registro e controle de ocorrências e apreensões. 