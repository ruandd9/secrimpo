# 🔄 Guia de Sincronização SECRIMPO

Este guia explica como implementar e usar o sistema de sincronização entre aplicações Electron locais e o servidor central FastAPI.

## 📋 Visão Geral

O sistema permite que múltiplos usuários com aplicações Electron locais sincronizem seus dados com um servidor central, mantendo:
- ✅ Funcionamento offline
- ✅ Prevenção de duplicação
- ✅ Identificação de usuários
- ✅ Histórico de sincronizações
- ✅ Interface amigável

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Electron App  │    │   Electron App  │    │   Electron App  │
│   (Usuário A)   │    │   (Usuário B)   │    │   (Usuário C)   │
│                 │    │                 │    │                 │
│  SQLite Local   │    │  SQLite Local   │    │  SQLite Local   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Servidor Central     │
                    │      (FastAPI)          │
                    │                         │
                    │  SQLite/Excel Central   │
                    └─────────────────────────┘
```

## 🚀 Implementação

### 1. Backend (FastAPI)

O backend já está implementado com os seguintes endpoints:

- `POST /sincronizar` - Sincroniza dados do cliente
- `GET /sincronizar/status/{usuario}` - Status de sincronização
- `GET /sincronizar/historico/{usuario}` - Histórico de sincronizações
- `GET /sincronizar/usuarios` - Lista usuários sincronizados
- `POST /sincronizar/teste` - Teste de conectividade

### 2. Frontend (Electron)

#### 2.1 Incluir o SyncManager

Adicione o arquivo `sync-manager.js` ao seu projeto:

```html
<script src="src/sync-manager.js"></script>
```

#### 2.2 Adicionar Interface de Status

Adicione esta barra de status ao seu HTML principal:

```html
<!-- Barra de status de sincronização -->
<div id="sync-status-bar" style="background: #f8f9fa; padding: 10px; border-bottom: 1px solid #ddd;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span id="connection-status">🔴 Offline</span>
            <span id="last-sync-info" style="margin-left: 20px; color: #6c757d;"></span>
        </div>
        <div>
            <input type="text" id="usuario-sync" placeholder="Seu nome/ID" style="margin-right: 10px; padding: 5px;">
            <button id="sync-button" onclick="syncApp.executarSincronizacao()" disabled>🔄 Sincronizar</button>
            <button onclick="syncApp.abrirTelaSincronizacao()">⚙️ Configurar</button>
        </div>
    </div>
</div>
```

#### 2.3 Incluir Integração

Adicione o arquivo de integração:

```html
<script src="src/sync-integration-example.js"></script>
```

### 3. Modificações no Banco Local

Adicione colunas UUID às suas tabelas SQLite locais:

```sql
-- Adicionar colunas UUID
ALTER TABLE policial ADD COLUMN uuid_local TEXT;
ALTER TABLE proprietario ADD COLUMN uuid_local TEXT;
ALTER TABLE ocorrencia ADD COLUMN uuid_local TEXT;
ALTER TABLE item_apreendido ADD COLUMN uuid_local TEXT;

-- Criar índices para performance
CREATE INDEX idx_policial_uuid ON policial(uuid_local);
CREATE INDEX idx_proprietario_uuid ON proprietario(uuid_local);
CREATE INDEX idx_ocorrencia_uuid ON ocorrencia(uuid_local);
```

### 4. Funções do Database Manager

Adicione estas funções ao seu database manager:

```javascript
// Gerar UUID
function generateUuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Adicionar UUID ao criar registro
async function createPolicial(dados) {
    dados.uuid_local = generateUuid();
    // ... resto da função de criação
}

// Obter dados completos para sincronização
async function getAllOcorrenciasCompletas() {
    // Implementar query com JOINs para obter dados relacionados
    // Ver exemplo em sync-integration-example.js
}

// Contar registros não sincronizados
async function getUnsyncedCount() {
    // Contar registros sem UUID ou não sincronizados
}
```

## 🧪 Testando o Sistema

### 1. Iniciar a API

```bash
cd backend
python start_api.py
```

### 2. Executar Testes

```bash
python test_sync_system.py
```

### 3. Testar Interface

Abra o arquivo `frontend/src/sync-ui.html` em um navegador ou integre ao seu app Electron.

## 📊 Exemplo de Uso

### 1. Configurar Usuário

```javascript
// Definir usuário
syncManager.setUsuario("agente_joao");
```

### 2. Sincronizar Dados

```javascript
// Sincronização manual
try {
    const resultado = await syncManager.sincronizar();
    console.log('Sincronização concluída:', resultado.message);
} catch (error) {
    console.error('Erro:', error.message);
}
```

### 3. Verificar Status

```javascript
// Obter status
const status = await syncManager.obterStatusSincronizacao();
console.log('Última sincronização:', status.ultima_sincronizacao);
```

## 🔧 Configuração Avançada

### 1. Sincronização Automática

```javascript
// Sincronizar automaticamente a cada hora
setInterval(async () => {
    if (syncManager.isOnline && syncManager.needsSync(1)) {
        await syncManager.sincronizar(false); // Sem UI de progresso
    }
}, 3600000); // 1 hora
```

### 2. Eventos de Dados

```javascript
// Quando criar novos dados
function onNovosDadosCriados(tipo, dados) {
    // Adicionar UUID
    dados.uuid_local = syncManager.generateUuid();
    
    // Salvar no banco local
    await dbManager.save(tipo, dados);
    
    // Notificar sistema de sync
    syncApp.onDataCreated(tipo, dados);
}
```

### 3. Configurar Servidor

```javascript
// Alterar URL do servidor
syncManager.serverUrl = 'http://192.168.1.100:8000';
```

## 📋 Formato dos Dados

### Estrutura de Sincronização

```json
{
    "usuario": "agente_joao",
    "client_uuid": "uuid-do-cliente",
    "timestamp_cliente": "2025-09-01T10:00:00",
    "dados": {
        "policiais": [
            {
                "uuid_local": "uuid-do-policial",
                "nome": "João Silva",
                "matricula": "12345",
                "graduacao": "Soldado",
                "unidade": "8ª CPR"
            }
        ],
        "proprietarios": [
            {
                "uuid_local": "uuid-do-proprietario",
                "nome": "Maria Santos",
                "documento": "123.456.789-00"
            }
        ],
        "ocorrencias": [
            {
                "uuid_local": "uuid-da-ocorrencia",
                "numero_genesis": "2025-0001",
                "unidade_fato": "8ª CPR",
                "data_apreensao": "2025-09-01",
                "lei_infringida": "Lei de Drogas",
                "artigo": "Art. 33",
                "policial_condutor": {
                    "nome": "João Silva",
                    "matricula": "12345",
                    "graduacao": "Soldado",
                    "unidade": "8ª CPR"
                },
                "itens_apreendidos": [
                    {
                        "especie": "Droga",
                        "item": "Maconha",
                        "quantidade": 1,
                        "descricao_detalhada": "Porção apreendida",
                        "proprietario": {
                            "nome": "Maria Santos",
                            "documento": "123.456.789-00"
                        }
                    }
                ]
            }
        ]
    }
}
```

## 🛠️ Solução de Problemas

### Erro: "Sem conexão com servidor"

1. Verifique se a API está rodando: `python backend/start_api.py`
2. Teste a URL: `http://127.0.0.1:8000`
3. Verifique firewall/antivírus

### Erro: "Usuário não definido"

1. Configure o usuário: `syncManager.setUsuario("seu_nome")`
2. Verifique se o campo de usuário está preenchido

### Dados não aparecem após sincronização

1. Verifique se os UUIDs estão sendo gerados
2. Confirme se os dados estão no formato correto
3. Verifique logs de erro no console

### Performance lenta

1. Limite a quantidade de dados por sincronização
2. Implemente paginação para grandes volumes
3. Otimize queries do banco local

## 📈 Monitoramento

### Logs do Servidor

```bash
# Ver logs da API
tail -f backend/logs/api.log
```

### Métricas de Sincronização

```javascript
// Obter estatísticas
const stats = await syncManager.obterStatusSincronizacao();
console.log('Total de sincronizações:', stats.total_sincronizacoes);
console.log('Registros sincronizados:', stats.total_registros_sincronizados);
```

## 🔒 Segurança

### Recomendações

1. **HTTPS em Produção**: Use HTTPS para comunicação
2. **Autenticação**: Implemente autenticação de usuários
3. **Validação**: Valide todos os dados recebidos
4. **Rate Limiting**: Limite requisições por usuário
5. **Backup**: Faça backup regular do banco central

### Exemplo de Autenticação

```javascript
// Adicionar token de autenticação
syncManager.authToken = "seu-token-jwt";

// Modificar requests para incluir token
headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${syncManager.authToken}`
}
```

## 🎯 Próximos Passos

1. **Teste com dados reais** em ambiente controlado
2. **Implemente autenticação** se necessário
3. **Configure backup automático** do servidor
4. **Monitore performance** com múltiplos usuários
5. **Documente procedimentos** para usuários finais

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique este guia primeiro
2. Execute os testes: `python test_sync_system.py`
3. Consulte os logs de erro
4. Documente o problema com detalhes

---

**Versão**: 1.0.0  
**Última atualização**: Setembro 2025