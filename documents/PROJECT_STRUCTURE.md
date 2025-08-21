# SECRIMPO - Estrutura do Projeto

Documentação completa da estrutura de arquivos e diretórios do projeto SECRIMPO.

## Estrutura Geral

```
secrimpo/
├── 📄 README.md                    # Documentação principal
├── 📄 CHANGELOG.md                 # Histórico de versões
├── 📄 LICENSE                      # Licença MIT
├── 📄 .gitignore                   # Arquivos ignorados pelo Git
├── 📄 package.json                 # Scripts npm do projeto
├── 📄 setup.py                     # Script de instalação automática
│
├── 📁 documents/                   # 📚 Documentação técnica
│   ├── 📄 README.md                # Índice da documentação
│   ├── 📄 NETWORK_SYNC_GUIDE.md    # Guia de sincronização em rede
│   ├── 📄 API_DOCUMENTATION.md     # Documentação da API
│   ├── 📄 QUICK_START.md           # Guia de início rápido
│   ├── 📄 TROUBLESHOOTING.md       # Solução de problemas
│   └── 📄 PROJECT_STRUCTURE.md     # Este arquivo
│
├── 📁 backend/                     # 🐍 API FastAPI
│   ├── 📄 app.py                   # Aplicação FastAPI principal
│   ├── 📄 start_api.py             # Script de inicialização
│   ├── 📄 test_api.py              # Visualizador de dados
│   ├── 📄 config.py                # Configurações
│   ├── 📄 requirements.txt         # Dependências Python
│   ├── 📄 .gitignore               # Ignores específicos do backend
│   ├── 📄 secrimpo.db              # Banco SQLite (gerado automaticamente)
│   └── 📁 services/                # Serviços de negócio
│       ├── 📄 crud_service.py      # Operações CRUD
│       └── 📄 excel_export.py      # Exportação Excel
│
├── 📁 frontend/                    # ⚡ Aplicação Electron
│   ├── 📄 main.js                  # Processo principal do Electron
│   ├── 📄 preload.js               # Script de preload (bridge)
│   ├── 📄 package.json             # Dependências Node.js
│   ├── 📄 .gitignore               # Ignores específicos do frontend
│   ├── 📁 src/                     # Código fonte da interface
│   │   ├── 📄 index.html           # Página principal
│   │   ├── 📄 styles.css           # Estilos CSS
│   │   └── 📄 app.js               # Lógica JavaScript
│   └── 📁 assets/                  # Recursos (logos, ícones)
│       └── 📄 placeholder.txt      # Placeholder para assets
│
└── 📁 models/ & database/          # 📚 Estrutura legada (mantida)
    ├── 📄 base.py                  # Base SQLAlchemy
    ├── 📄 ocorrencia.py            # Modelo Ocorrência
    ├── 📄 policial.py              # Modelo Policial
    ├── 📄 proprietario.py          # Modelo Proprietário
    ├── 📄 item_apreendido.py       # Modelo Item Apreendido
    └── 📄 db.py                    # Configuração do banco
```

## Descrição dos Componentes

### 📄 Arquivos Raiz

#### README.md
- Documentação principal do projeto
- Visão geral, instalação e uso básico
- Links para documentação detalhada

#### CHANGELOG.md
- Histórico de versões
- Registro de mudanças e melhorias
- Notas de release

#### LICENSE
- Licença MIT do projeto
- Termos de uso e distribuição

#### .gitignore
- Arquivos e pastas ignorados pelo Git
- Configurações para Python, Node.js e sistema

#### package.json
- Scripts npm para facilitar desenvolvimento
- Comandos para iniciar backend e frontend
- Metadados do projeto

#### setup.py
- Script de instalação automática
- Verifica pré-requisitos
- Instala dependências automaticamente

### 📁 documents/ - Documentação

#### Propósito
Centralizar toda a documentação técnica do projeto em arquivos Markdown organizados.

#### Conteúdo
- **README.md**: Índice de toda documentação
- **NETWORK_SYNC_GUIDE.md**: Configuração multi-usuário
- **API_DOCUMENTATION.md**: Endpoints e exemplos da API
- **QUICK_START.md**: Guia para começar rapidamente
- **TROUBLESHOOTING.md**: Solução de problemas comuns
- **PROJECT_STRUCTURE.md**: Este arquivo

#### Padrões
- Formato Markdown (.md)
- Estrutura consistente com seções padronizadas
- Exemplos de código funcionais
- Links internos entre documentos

### 📁 backend/ - API FastAPI

#### Arquivos Principais

**app.py**
- Aplicação FastAPI principal
- Definição de todos os endpoints REST
- Configuração CORS e middleware
- Modelos SQLAlchemy integrados

**start_api.py**
- Script para inicializar o servidor
- Configurações de host, porta e logs
- Mensagens informativas de startup

**test_api.py**
- Visualizador de dados do banco
- Diagnóstico de conectividade
- Estatísticas do sistema

**config.py**
- Configurações centralizadas
- URLs de banco, diretórios, etc.
- Configurações específicas por ambiente

**requirements.txt**
- Dependências Python necessárias
- Versões específicas para compatibilidade

#### Subpasta services/

**crud_service.py**
- Operações CRUD para todas as entidades
- Lógica de negócio centralizada
- Validações e tratamento de erros

**excel_export.py**
- Serviços de exportação para Excel
- Formatação profissional de relatórios
- Múltiplos tipos de exportação

#### Arquivos Gerados

**secrimpo.db**
- Banco SQLite gerado automaticamente
- Contém todas as tabelas e dados
- Criado na primeira execução da API

### 📁 frontend/ - Aplicação Electron

#### Arquivos Principais

**main.js**
- Processo principal do Electron
- Configuração da janela da aplicação
- Gerenciamento do ciclo de vida

**preload.js**
- Script de preload para segurança
- Bridge entre renderer e main process
- Exposição segura de APIs

**package.json**
- Dependências Node.js
- Scripts de build e desenvolvimento
- Configurações do Electron

#### Subpasta src/

**index.html**
- Página principal da aplicação
- Estrutura HTML do formulário
- Integração com Font Awesome

**styles.css**
- Estilos CSS da aplicação
- Design responsivo e profissional
- Cores institucionais da PMDF

**app.js**
- Lógica JavaScript da aplicação
- Comunicação com a API
- Validações e interações do usuário

#### Subpasta assets/

**placeholder.txt**
- Placeholder para recursos visuais
- Instruções para adicionar logos
- Ícones e imagens da aplicação

### 📁 models/ & database/ - Estrutura Legada

#### Propósito
Mantida para compatibilidade com versões anteriores e referência.

#### Conteúdo
- **base.py**: Base declarativa SQLAlchemy
- **ocorrencia.py**: Modelo da entidade Ocorrência
- **policial.py**: Modelo da entidade Policial
- **proprietario.py**: Modelo da entidade Proprietário
- **item_apreendido.py**: Modelo da entidade Item Apreendido
- **db.py**: Configuração original do banco

## Fluxo de Dados

### 1. Inicialização
```
setup.py → Instala dependências
start_api.py → Inicia FastAPI
main.js → Inicia Electron
```

### 2. Operação Normal
```
Frontend (Electron) → API (FastAPI) → Banco (SQLite)
     ↑                    ↓
   app.js ←── JSON ←── crud_service.py
```

### 3. Exportação
```
Frontend → API → excel_export.py → Arquivo .xlsx
```

## Padrões de Desenvolvimento

### Nomenclatura de Arquivos
- **Python**: snake_case (ex: `crud_service.py`)
- **JavaScript**: camelCase para variáveis, kebab-case para arquivos
- **Documentação**: UPPER_CASE.md (ex: `README.md`)

### Estrutura de Código
- **Backend**: Separação clara entre API, serviços e modelos
- **Frontend**: Separação entre lógica, apresentação e estilos
- **Documentação**: Estrutura consistente com seções padronizadas

### Versionamento
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Tags Git**: Para releases importantes
- **CHANGELOG.md**: Registro detalhado de mudanças

## Configurações de Ambiente

### Desenvolvimento
```bash
# Backend
cd backend
python start_api.py

# Frontend
cd frontend
npm run dev
```

### Produção
```bash
# Backend (modo servidor)
cd backend
python start_api.py --host 0.0.0.0

# Frontend (build)
cd frontend
npm run build
```

### Testes
```bash
# Visualizar dados
cd backend
python test_api.py

# Diagnóstico completo
python setup.py --diagnose
```

## Dependências Principais

### Backend (Python)
- **FastAPI**: Framework web moderno
- **SQLAlchemy**: ORM para banco de dados
- **Pandas**: Manipulação e exportação de dados
- **Pydantic**: Validação de dados
- **Uvicorn**: Servidor ASGI

### Frontend (Node.js)
- **Electron**: Framework para aplicações desktop
- **Font Awesome**: Ícones profissionais
- **Axios**: Cliente HTTP (via preload)

## Segurança

### Práticas Implementadas
- **Context Isolation**: Electron com isolamento de contexto
- **Preload Scripts**: Bridge segura entre processos
- **CORS**: Configurado para origens específicas
- **Validação**: Pydantic para validação de entrada

### Recomendações para Produção
- Implementar autenticação JWT
- Configurar HTTPS
- Limitar CORS a domínios específicos
- Implementar rate limiting

## Manutenção

### Atualizações
- **Dependências**: Atualizar regularmente via `pip` e `npm`
- **Documentação**: Manter sincronizada com código
- **Testes**: Executar após mudanças significativas

### Backup
- **Banco de dados**: `backend/secrimpo.db`
- **Configurações**: Arquivos de config personalizados
- **Documentação**: Pasta `documents/` completa

### Monitoramento
- **Logs**: Console da API e frontend
- **Performance**: Uso de CPU/RAM via task manager
- **Integridade**: Verificação periódica do banco

---

**Última atualização:** 21/08/2024  
**Versão da estrutura:** 1.0.0  
**Compatível com:** SECRIMPO v1.0.0+