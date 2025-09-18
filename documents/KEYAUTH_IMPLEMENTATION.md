# Implementação KeyAuth no SECRIMPO

## 🎯 Visão Geral

O SECRIMPO agora inclui **sistema de autenticação KeyAuth** fornecendo controle de acesso seguro para dados policiais. Esta implementação oferece:

- **Autenticação baseada em licença** usando KeyAuth
- **Permissões baseadas em função** (Admin, Agente, Visualizador)
- **Registro de auditoria** para todas as ações do usuário
- **Endpoints de API seguros** com verificações de permissão
- **Integração limpa do frontend** com interface de login

## 🔧 Instalação e Configuração

### 1. Instalar Dependências

```bash
# Instalar dependências Python
pip install -r backend/requirements.txt

# KeyAuth está incluído no requirements.txt
```

### 2. Configurar Credenciais KeyAuth

**Opção A: Configuração Interativa (Recomendado)**
```bash
python setup_keyauth.py
```

**Opção B: Configuração Manual**
Crie o arquivo `.env` na raiz do projeto:
```env
KEYAUTH_OWNER_ID=seu_owner_id_aqui
KEYAUTH_SECRET=seu_secret_aqui
KEYAUTH_APP_NAME=SECRIMPO
```

### 3. Criar Aplicação KeyAuth

1. Acesse [keyauth.cc](https://keyauth.cc)
2. Crie uma conta e faça login
3. Crie uma nova aplicação chamada "SECRIMPO"
4. Copie o Owner ID e Secret para seu arquivo `.env`

### 4. Configurar Níveis de Assinatura

No seu painel KeyAuth, crie estas assinaturas:

- **admin** - Acesso total ao sistema
- **agent** - Acesso para criar/editar
- **viewer** - Acesso somente leitura
- **restricted** - Acesso mínimo

## 📁 Estrutura de Arquivos

```
secrimpo/
├── backend/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── keyauth_config.py     # Gerenciador KeyAuth
│   │   └── middleware.py         # Middleware de auth e decoradores
│   ├── app.py                    # Endpoints da API protegidos
│   └── requirements.txt          # Atualizado com deps KeyAuth
├── frontend/src/
│   ├── auth.js                   # Gerenciador de auth frontend
│   ├── login.html                # Interface de login
│   └── index.html                # App principal (protegido)
├── setup_keyauth.py              # Script de configuração
└── .env                          # Credenciais KeyAuth (criar este)
```

## 🔒 Sistema de Permissões

### Níveis de Assinatura

| Permissão | Admin | Agente | Visualizador | Restrito |
|------------|-------|-------|--------|------------|
| `create_occurrence` | ✅ | ✅ | ❌ | ❌ |
| `edit_occurrence` | ✅ | ✅ | ❌ | ❌ |
| `delete_occurrence` | ✅ | ❌ | ❌ | ❌ |
| `view_all_occurrences` | ✅ | ✅ | ✅ | ❌ |
| `export_reports` | ✅ | ✅ | ❌ | ❌ |
| `view_statistics` | ✅ | ✅ | ✅ | ❌ |
| `manage_users` | ✅ | ❌ | ❌ | ❌ |
| `system_config` | ✅ | ❌ | ❌ | ❌ |

### Endpoints Protegidos

Todas as operações CRUD agora requerem autenticação:

```python
# Exemplo: Criar uma ocorrência requer permissão
@app.post("/ocorrencias/")
@require_permission("create_occurrence")
async def criar_ocorrencia(
    ocorrencia: OcorrenciaCreate, 
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(verify_license)
):
    # Lógica do endpoint com contexto do usuário
    auth_manager.log_user_action(auth.username, "CREATE_OCORRENCIA", f"Genesis: {ocorrencia.numero_genesis}")
    # ...
```

## 🖥️ Integração Frontend

### Fluxo de Autenticação

1. **Página de Login** (`login.html`) - Usuário insere chave de licença
2. **Validação** - KeyAuth valida licença e retorna permissões
3. **App Principal** (`index.html`) - Protegido com verificações de auth
4. **Logout** - Limpa credenciais e redireciona

### Uso no Frontend

```javascript
// Verificar se usuário está autenticado
if (!await authManager.checkAuthStatus()) {
    window.location.href = 'login.html';
    return;
}

// Fazer chamadas de API autenticadas
const response = await axios.post('/ocorrencias/', data);

// Verificar permissões antes de mostrar elementos da UI
if (authManager.hasPermission('export_reports')) {
    document.getElementById('export-btn').style.display = 'block';
}

// Obter informações do usuário
const userInfo = authManager.getUserInfo();
console.log(`Bem-vindo ${userInfo.username}!`);
```

## 🚀 Executando o Sistema

### 1. Iniciar API Backend

```bash
cd backend
python start_api.py
```

### 2. Acessar Frontend

**Com Autenticação:**
- Abrir: http://localhost:8000 (redireciona para login.html)
- Inserir sua chave de licença KeyAuth
- Acessar sistema principal após login bem-sucedido

**Teste Direto da API:**
- Documentação da API: http://localhost:8000/docs
- Verificação de Saúde: http://localhost:8000/

## 🛡️ Recursos de Segurança

### Registro de Auditoria

Todas as ações do usuário são registradas:
```
[2025-09-17 10:30:15] john_doe: CREATE_OCORRENCIA - Genesis: 2025-001
[2025-09-17 10:32:20] jane_admin: EXPORT_COMPLETE_REPORT - Period: 2025-01-01 to 2025-09-17
[2025-09-17 10:35:10] viewer_user: PERMISSION_DENIED - Required: delete_occurrence, Has: viewer
```

### Validação de Token

- Todas as requisições da API requerem token Bearer válido
- Tokens validados contra KeyAuth a cada requisição
- Logout automático na expiração do token

### Aplicação de Permissões

- Decoradores protegem endpoints: `@require_permission("nome_permissao")`
- Frontend oculta elementos da UI não autorizados
- Validação server-side previne escalação de privilégios

## 🔧 Personalização

### Adicionando Novas Permissões

1. **Atualizar definições de permissão** em `keyauth_config.py`:
```python
"nova_funcao": {
    "permissao_customizada": True,
    # ... outras permissões
}
```

2. **Proteger endpoints** com nova permissão:
```python
@app.post("/endpoint-customizado/")
@require_permission("permissao_customizada")
async def endpoint_customizado(auth: AuthContext = Depends(verify_license)):
    # Implementação
```

3. **Atualizar frontend** para verificar nova permissão:
```javascript
if (authManager.hasPermission('permissao_customizada')) {
    // Mostrar/ocultar elementos da UI
}
```

### Lógica de Validação Customizada

Estender classe `AuthContext` em `middleware.py`:
```python
class AuthContext:
    def can_access_data_by_unit(self, unit: str) -> bool:
        # Lógica de negócio customizada
        if self.subscription == 'admin':
            return True
        return self.user_data.get('assigned_unit') == unit
```

## 🧪 Testes

### Testar Autenticação

```bash
# Testar com script de configuração
python setup_keyauth.py

# Testar endpoint da API
curl -H "Authorization: Bearer SUA_CHAVE_LICENCA" http://localhost:8000/auth/validate
```

### Testar Permissões

```bash
# Testar acesso admin
curl -H "Authorization: Bearer LICENCA_ADMIN" http://localhost:8000/export/relatorio_completo?data_inicio=2025-01-01&data_fim=2025-12-31

# Testar acesso não autorizado (deve retornar 403)
curl -H "Authorization: Bearer LICENCA_VIEWER" http://localhost:8000/export/relatorio_completo?data_inicio=2025-01-01&data_fim=2025-12-31
```

## 🚨 Solução de Problemas

### Problemas Comuns

**"KeyAuth initialization failed"**
- Verificar Owner ID e Secret no `.env`
- Verificar se aplicação KeyAuth existe
- Garantir conexão com internet para API KeyAuth

**"Invalid or expired license key"**
- Verificar se chave de licença está correta
- Verificar se licença expirou no painel KeyAuth
- Garantir que licença pertence à aplicação correta

**Erros de "Permission denied"**
- Verificar nível de assinatura do usuário
- Verificar se permissão está corretamente atribuída à assinatura
- Verificar se decorador de permissão corresponde aos requisitos do endpoint

### Modo Debug

Habilitar logging detalhado atualizando `keyauth_config.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Referência da API

### Endpoints de Autenticação

- `POST /auth/validate` - Validar licença e obter permissões
- `GET /auth/user-info` - Obter informações do usuário atual

### Endpoints Protegidos

Todos os endpoints CRUD agora requerem autenticação:
- `/policiais/*` - Requer: `view_all_occurrences` ou `create_occurrence`
- `/proprietarios/*` - Requer: `view_all_occurrences` ou `create_occurrence`  
- `/ocorrencias/*` - Requer: `view_all_occurrences` ou `create_occurrence`
- `/itens/*` - Requer: `view_all_occurrences` ou `create_occurrence`
- `/export/*` - Requer: `export_reports`
- `/estatisticas/*` - Requer: `view_statistics`

## ✅ Melhores Práticas

1. **Credenciais Seguras**: Nunca commitar `.env` para controle de versão
2. **Gerenciamento de Licenças**: Revisar e rotacionar chaves de licença regularmente
3. **Revisão de Permissões**: Auditar permissões de usuário periodicamente
4. **Monitorar Logs**: Verificar logs de auditoria para atividade suspeita
5. **Atualizar Dependências**: Manter biblioteca KeyAuth atualizada

---

**🎉 Seu sistema SECRIMPO agora está seguro com autenticação KeyAuth!**

O sistema fornece segurança robusta mantendo facilidade de uso. Os usuários simplesmente inserem sua chave de licença uma vez e podem acessar o sistema baseado em suas permissões atribuídas.