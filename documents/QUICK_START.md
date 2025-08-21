# SECRIMPO - Guia de Início Rápido

Guia prático para começar a usar o SECRIMPO em poucos minutos.

## Pré-requisitos

- Windows 10+ ou Linux Ubuntu 18+
- Python 3.8+ instalado
- Node.js 16+ instalado
- 2GB de espaço livre em disco

## Instalação Rápida

### 1. Download e Configuração
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd secrimpo

# Execute o setup automático
python setup.py
```

### 2. Iniciar o Sistema
```bash
# Terminal 1: Iniciar API
cd backend
python start_api.py

# Terminal 2: Iniciar Interface
cd frontend
npm start
```

### 3. Primeiro Acesso
- A interface abrirá automaticamente
- API estará disponível em: http://127.0.0.1:8000
- Documentação em: http://127.0.0.1:8000/docs

## Primeiro Uso

### 1. Cadastrar um Policial
1. Vá para a seção "DADOS DO POLICIAL"
2. Preencha:
   - **Nome:** João Silva
   - **Matrícula:** 12345
   - **Graduação:** Soldado (selecione no dropdown)
   - **Unidade:** 8ª CPR (selecione no dropdown)

### 2. Cadastrar um Proprietário
1. Vá para "DADOS DO PROPRIETÁRIO"
2. Selecione **Tipo de Documento:** CPF
3. Digite o **Documento:** 12345678900 (será formatado automaticamente)
4. **Nome:** Maria Santos

### 3. Registrar uma Ocorrência
1. Preencha "DADOS DA OCORRÊNCIA":
   - **Número Gênesis:** 2024001234
   - **Unidade do Fato:** Centro
   - **Data da Apreensão:** (data atual já preenchida)
   - **Lei Infringida:** Lei 11.343/06
   - **Artigo:** Art. 28

### 4. Adicionar Item Apreendido
1. Na seção "ITENS APREENDIDOS":
   - **Espécie:** Entorpecente
   - **Item:** Maconha (aparece automaticamente)
   - **Quantidade:** 1
   - **Descrição:** Pequena porção de substância análoga à maconha

### 5. Salvar o Registro
1. Clique em "Salvar em PNG"
2. Aguarde a confirmação de sucesso
3. Os dados serão salvos no banco SQLite

## Funcionalidades Principais

### Busca Automática
- **Policial:** Digite a matrícula e pressione Tab
- **Proprietário:** Digite o documento e pressione Tab
- Sistema busca automaticamente dados existentes

### Validação em Tempo Real
- **CPF:** Validação com dígitos verificadores
- **RG:** Validação de formato
- **Campos obrigatórios:** Destacados em vermelho se vazios

### Múltiplos Itens
- Clique em "Adicionar Item" para mais itens
- Cada item pode ter proprietário diferente
- Botão de remoção aparece quando há múltiplos itens

## Atalhos Úteis

| Ação | Atalho |
|------|--------|
| Salvar formulário | Ctrl + S |
| Novo registro | Ctrl + N |
| Buscar policial | Tab (após digitar matrícula) |
| Buscar proprietário | Tab (após digitar documento) |
| Adicionar item | Ctrl + + |

## Visualizar Dados Salvos

### Via Terminal
```bash
cd backend
python test_api.py
```

### Via Navegador
- Acesse: http://127.0.0.1:8000/docs
- Use a interface Swagger para consultar dados

### Via Interface
- Os dados aparecem automaticamente na busca
- Digite matrícula/documento para carregar registros existentes

## Solução de Problemas Comuns

### API não inicia
```bash
# Verificar se porta 8000 está livre
netstat -an | findstr :8000

# Se estiver ocupada, matar processo
taskkill /f /im python.exe
```

### Frontend não conecta
1. Verifique se API está rodando
2. Teste: http://127.0.0.1:8000 no navegador
3. Reinicie o frontend: Ctrl+C e `npm start`

### Banco de dados corrompido
```bash
# Backup do banco atual
copy backend\secrimpo.db backend\secrimpo_backup.db

# Remover banco corrompido
del backend\secrimpo.db

# Reiniciar API (criará novo banco)
cd backend && python start_api.py
```

### Campos não salvam
1. Verifique se todos os campos obrigatórios estão preenchidos
2. Campos em vermelho indicam erro de validação
3. CPF/RG devem estar válidos (indicador verde)

## Próximos Passos

### Para Uso Individual
- Continue usando normalmente
- Dados ficam salvos localmente
- Faça backup regular do arquivo `backend/secrimpo.db`

### Para Uso em Rede
- Consulte [NETWORK_SYNC_GUIDE.md](./NETWORK_SYNC_GUIDE.md)
- Configure sincronização entre múltiplos PCs
- Implemente backup centralizado

### Para Personalização
- Modifique graduações em `frontend/src/index.html`
- Adicione novas unidades no mesmo arquivo
- Customize espécies/itens em `frontend/src/app.js`

## Comandos Úteis

### Verificar Status
```bash
# Status da API
curl http://127.0.0.1:8000/

# Estatísticas do banco
curl http://127.0.0.1:8000/estatisticas/
```

### Backup Manual
```bash
# Backup do banco
copy backend\secrimpo.db "backup\secrimpo_$(date +%Y%m%d).db"

# Backup completo
tar -czf secrimpo_backup.tar.gz backend/ frontend/ documents/
```

### Atualização
```bash
# Atualizar dependências Python
cd backend && pip install -r requirements.txt --upgrade

# Atualizar dependências Node.js
cd frontend && npm update
```

## Suporte

### Documentação Completa
- [README.md](../README.md) - Visão geral
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API detalhada
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Solução de problemas

### Logs do Sistema
- **API:** Console onde rodou `python start_api.py`
- **Frontend:** F12 → Console no Electron
- **Arquivos:** `backend/secrimpo_server.log` (se configurado)

### Contato
- Abra issue no repositório GitHub
- Consulte FAQ.md para dúvidas comuns
- Entre em contato com a equipe de desenvolvimento

---

**Tempo estimado de setup:** 5-10 minutos  
**Primeira ocorrência:** 2-3 minutos  
**Nível de dificuldade:** Iniciante  

🎉 **Parabéns! Você está pronto para usar o SECRIMPO!**