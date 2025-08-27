# Changelog - SECRIMPO

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2024-08-21

### ✨ Adicionado
- **Backend FastAPI completo**
  - API REST com todos os endpoints CRUD
  - Modelos SQLAlchemy para Policial, Proprietário, Ocorrência e Item
  - Validação Pydantic para todos os dados
  - Serviços de exportação Excel com Pandas
  - Banco SQLite com criação automática de tabelas
  - Sistema de estatísticas e relatórios

- **Frontend Electron moderno**
  - Interface desktop nativa multiplataforma
  - Formulário completo replicando design original
  - Validação em tempo real de todos os campos
  - Máscaras automáticas para CPF/RG
  - Dropdowns inteligentes para espécies/itens
  - Auto-complete para policiais e proprietários
  - Feedback visual para ações do usuário

- **Funcionalidades avançadas**
  - Graduações predefinidas da Polícia Militar
  - Unidades específicas (8ª, 10ª, 16ª CPR)
  - Validação completa de CPF com dígitos verificadores
  - Busca automática por matrícula e documento
  - Gestão dinâmica de múltiplos itens apreendidos
  - Sistema de mensagens e loading

- **Infraestrutura de desenvolvimento**
  - Scripts de inicialização automatizados
  - Visualizador de dados do banco
  - Testes automatizados da API
  - Configuração completa do Electron
  - Sistema de build e distribuição

### 🛠️ Técnico
- **Backend**: FastAPI + SQLAlchemy + Pandas + SQLite
- **Frontend**: Electron + HTML5 + CSS3 + JavaScript ES6+
- **Comunicação**: API REST com validação Pydantic
- **Banco**: SQLite com relacionamentos complexos
- **Exportação**: Excel com formatação profissional

### 📋 Estrutura de Dados
- **Policiais**: Nome, matrícula, graduação, unidade
- **Proprietários**: Nome, documento (CPF/RG validado)
- **Ocorrências**: Gênesis, unidade, data, lei, artigo
- **Itens**: Espécie, item, quantidade, descrição detalhada

### 🎯 Interface
- Design fiel ao sistema original
- Cores institucionais da PMDF
- Responsividade para diferentes telas
- Acessibilidade e usabilidade otimizadas
- Feedback visual em tempo real

### 📦 Entrega
- Aplicação desktop completa
- API REST documentada
- Banco de dados local
- Sistema de exportação
- Documentação completa
- Scripts de setup automatizado

---

## Próximas Versões Planejadas

## [1.1.0] - 2024-08-27

### ✨ Adicionado
- **🗂️ Sistema de Pasta Compartilhada Multi-Usuário**
  - Configuração automática de armazenamento compartilhado
  - Suporte para múltiplos usuários simultâneos (até 10)
  - Sincronização em tempo real entre diferentes PCs
  - Backup automático centralizado

- **🛠️ Ferramentas de Configuração**
  - `setup_shared_folder.py` - Configurador interativo de pasta compartilhada
  - `test_shared_setup.py` - Teste completo de configuração
  - `backend/diagnostico_compartilhado.py` - Diagnóstico avançado
  - `backend/shared_storage.py` - Gerenciador de armazenamento

- **📋 Opções de Compartilhamento**
  - Pasta local compartilhada (Windows SMB/Linux Samba)
  - Servidor de arquivos de rede (\\servidor\pasta)
  - Unidade mapeada (Z:\pasta)
  - Detecção automática de pastas existentes

- **🔧 Melhorias Técnicas**
  - SQLite em modo WAL para melhor concorrência
  - Configuração automática de timeouts e cache
  - Sistema de fallback para modo local
  - Monitoramento de conectividade em tempo real

- **📊 Monitoramento e Diagnóstico**
  - Teste de performance do banco de dados
  - Verificação de integridade automática
  - Relatórios de diagnóstico em JSON
  - Logs centralizados de sistema

### 🛠️ Modificado
- **Configuração do Backend**
  - `config.py` atualizado para suporte a armazenamento compartilhado
  - `app.py` com detecção automática de modo (local/compartilhado)
  - Engine SQLAlchemy otimizada para rede

- **Documentação Expandida**
  - `README.md` com seção de pasta compartilhada
  - `GUIA_PASTA_COMPARTILHADA.md` - Guia completo de uso
  - Instruções detalhadas para cada cenário de uso

### 🎯 Casos de Uso Suportados
- **Escritório Pequeno (2-5 PCs)**: Pasta local compartilhada
- **Escritório com Servidor (5+ PCs)**: Servidor de arquivos
- **Unidade Mapeada**: Integração com infraestrutura existente
- **Detecção Automática**: Para ambientes já configurados

### 📈 Benefícios
- ✅ **Colaboração**: Múltiplos usuários veem os mesmos dados
- ✅ **Sincronização**: Automática e em tempo real
- ✅ **Backup**: Centralizado e automático
- ✅ **Facilidade**: Configuração em 5 minutos
- ✅ **Compatibilidade**: Funciona com infraestrutura existente

### [1.2.0] - Planejado
- [ ] Importação de dados CSV/Excel
- [ ] Relatórios PDF personalizados
- [ ] Sistema de usuários e permissões
- [ ] Dashboard com gráficos

### [1.2.0] - Planejado
- [ ] Dashboard com gráficos
- [ ] Busca avançada e filtros
- [ ] Histórico de alterações
- [ ] Notificações e lembretes
- [ ] Integração com impressoras

### [2.0.0] - Futuro
- [ ] Versão web responsiva
- [ ] API para integração externa
- [ ] Sistema de auditoria completo
- [ ] Módulo de relatórios avançados
- [ ] Suporte a múltiplas unidades

---

**Legenda:**
- ✨ Adicionado: Novas funcionalidades
- 🛠️ Modificado: Mudanças em funcionalidades existentes
- 🐛 Corrigido: Correções de bugs
- 🗑️ Removido: Funcionalidades removidas
- 🔒 Segurança: Correções de segurança