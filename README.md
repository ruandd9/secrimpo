# SECRIMPO - Sistema de Registro de Ocorrências

Sistema completo para registro de ocorrências policiais, itens apreendidos e geração automática de relatórios, desenvolvido especificamente para agentes SECRIMPO.

## Visão Geral

O SECRIMPO é um sistema moderno e eficiente que combina:
- **Backend FastAPI** para API REST robusta
- **Frontend Electron** para interface desktop nativa
- **Banco SQLite** para armazenamento local
- **Exportação Excel** para relatórios profissionais

### Funcionalidades Principais

- **Cadastro completo** de ocorrências policiais
- **Gestão de policiais** com graduações predefinidas
- **Registro de proprietários** com validação de documentos
- **Itens apreendidos** com categorização inteligente
- **Exportação automática** para Excel
- **Busca e validação** em tempo real
- **Armazenamento local** sem necessidade de internet

## Tecnologias Utilizadas

### Backend
- **FastAPI** - API REST moderna e rápida
- **SQLAlchemy** - ORM para banco de dados
- **Pandas** - Manipulação e exportação de dados
- **Pydantic** - Validação de dados
- **SQLite** - Banco de dados local

### Frontend
- **Electron** - Aplicação desktop multiplataforma
- **HTML5/CSS3** - Interface moderna e responsiva
- **JavaScript ES6+** - Lógica da aplicação
- **Axios** - Comunicação com API

## Estrutura do Projeto

```
secrimpo/
├── backend/                     # API FastAPI
│   ├── app.py                   # Aplicação principal
│   ├── start_api.py             # Script de inicialização
│   ├── test_api.py              # Visualizador de dados
│   ├── requirements.txt         # Dependências Python
│   ├── services/                # Serviços de negócio
│   │   ├── crud_service.py      # Operações CRUD
│   │   └── excel_export.py      # Exportação Excel
│   └── secrimpo.db             # Banco SQLite (gerado automaticamente)
│
├── frontend/                    # Aplicação Electron
│   ├── main.js                  # Processo principal
│   ├── preload.js               # Bridge segura
│   ├── package.json             # Dependências Node.js
│   ├── src/                     # Interface do usuário
│   │   ├── index.html           # Página principal
│   │   ├── styles.css           # Estilos CSS
│   │   └── app.js               # Lógica JavaScript
│   └── assets/                  # Recursos (logos, ícones)
│
├── models/                      # Modelos SQLAlchemy (legado)
├── database/                    # Configuração DB (legado)
├── .gitignore                   # Arquivos ignorados
└── README.md                    # Este arquivo
```

## Instalação e Execução

### Pré-requisitos
- Python 3.8+ instalado
- Node.js 16+ instalado
- Git instalado

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd secrimpo
```

### 2. Configure o Backend
```bash
# Entre na pasta backend
cd backend

# Instale as dependências Python
pip install -r requirements.txt

# Inicie a API
python start_api.py
```

### 3. Configure o Frontend
```bash
# Em outro terminal, entre na pasta frontend
cd frontend

# Instale as dependências Node.js
npm install

# Inicie a aplicação Electron
npm start
```

### 4. Acesse o Sistema
- **Interface Desktop**: Abre automaticamente com o Electron
- **API Documentation**: http://127.0.0.1:8000/docs
- **API Health Check**: http://127.0.0.1:8000/

## Como Usar

### Preenchimento do Formulário

1. **Dados da Ocorrência**
   - Número Gênesis
   - Unidade do Fato
   - Data da Apreensão
   - Lei Infringida
   - Artigo

2. **Itens Apreendidos**
   - Selecione a espécie (dropdown inteligente)
   - Escolha o item específico
   - Informe quantidade e descrição
   - Adicione múltiplos itens

3. **Dados do Proprietário**
   - Selecione tipo de documento (CPF/RG)
   - Digite o documento (máscara automática)
   - Informe o nome
   - Busca automática por documento

4. **Dados do Policial**
   - Nome do policial
   - Matrícula
   - Graduação (dropdown predefinido)
   - Unidade (8ª, 10ª ou 16ª CPR)
   - Busca automática por matrícula

### Recursos Especiais

- **Validação em Tempo Real**: CPF/RG validados automaticamente
- **Auto-complete**: Busca policiais e proprietários existentes
- **Máscaras Inteligentes**: Formatação automática de documentos
- **Dropdowns Inteligentes**: Itens mudam baseado na espécie
- **Feedback Visual**: Indicadores de sucesso/erro

## Testes e Desenvolvimento

### Visualizar Dados do Banco
```bash
cd backend
python test_api.py
```

### Testar API Manualmente
```bash
# Health check
curl http://127.0.0.1:8000/

# Listar policiais
curl http://127.0.0.1:8000/policiais/

# Estatísticas
curl http://127.0.0.1:8000/estatisticas/
```

### Desenvolvimento Frontend
```bash
cd frontend
npm run dev  # Inicia com DevTools aberto
```

## Exportação de Dados

O sistema oferece múltiplas opções de exportação:

- **Relatório Completo**: Todas as ocorrências por período
- **Resumo Mensal**: Estatísticas mensais
- **Por Policial**: Relatório individual
- **Estatísticas**: Análises detalhadas

## Configuração

### Variáveis de Ambiente
- `API_HOST`: Host da API (padrão: 127.0.0.1)
- `API_PORT`: Porta da API (padrão: 8000)
- `DATABASE_URL`: URL do banco SQLite

### Personalização
- **Unidades**: Edite as opções em `frontend/src/index.html`
- **Graduações**: Modifique o dropdown de graduações
- **Espécies/Itens**: Atualize o mapeamento em `frontend/src/app.js`

## Troubleshooting

### API não conecta
```bash
# Verifique se a API está rodando
curl http://127.0.0.1:8000/

# Reinicie a API
cd backend && python start_api.py
```

### Frontend não abre
```bash
# Reinstale dependências
cd frontend && npm install

# Verifique logs
npm start
```

### Banco de dados corrompido
```bash
# Remova o banco (CUIDADO: perde todos os dados)
rm backend/secrimpo.db

# Reinicie a API para recriar
cd backend && python start_api.py
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto é livre para uso acadêmico e institucional. Consulte o arquivo LICENSE para mais detalhes.

## Suporte

Para suporte técnico ou dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação da API em `/docs`
- Verifique os logs da aplicação

---

**Desenvolvido para facilitar o trabalho dos agentes SECRIMPO no registro e controle de ocorrências e apreensões.** 