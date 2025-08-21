# SECRIMPO - Documentação da API

Documentação completa da API REST do sistema SECRIMPO desenvolvida em FastAPI.

## Visão Geral

A API SECRIMPO fornece endpoints RESTful para gerenciar:
- Policiais e suas informações
- Proprietários de itens apreendidos
- Ocorrências policiais
- Itens apreendidos
- Relatórios e estatísticas

**Base URL:** `http://127.0.0.1:8000` (local) ou `http://IP-SERVIDOR:8000` (rede)

## Autenticação

Atualmente a API não requer autenticação. Para ambientes de produção, considere implementar:
- JWT tokens
- API keys
- OAuth 2.0

## Endpoints Principais

### Health Check
```http
GET /
```
Verifica se a API está funcionando.

**Resposta:**
```json
{
  "message": "SECRIMPO API está funcionando!",
  "version": "1.0.0"
}
```

### Estatísticas Gerais
```http
GET /estatisticas/
```
Retorna estatísticas gerais do sistema.

**Resposta:**
```json
{
  "total_ocorrencias": 10,
  "total_policiais": 5,
  "total_proprietarios": 8,
  "total_itens": 25
}
```

## Endpoints de Policiais

### Listar Policiais
```http
GET /policiais/?skip=0&limit=100
```

### Criar Policial
```http
POST /policiais/
Content-Type: application/json

{
  "nome": "João Silva",
  "matricula": "12345",
  "graduacao": "Soldado",
  "unidade": "8ª CPR"
}
```

### Obter Policial
```http
GET /policiais/{policial_id}
```

### Atualizar Policial
```http
PUT /policiais/{policial_id}
Content-Type: application/json

{
  "nome": "João Silva Santos",
  "graduacao": "Cabo"
}
```

### Deletar Policial
```http
DELETE /policiais/{policial_id}
```

## Endpoints de Proprietários

### Listar Proprietários
```http
GET /proprietarios/?skip=0&limit=100
```

### Criar Proprietário
```http
POST /proprietarios/
Content-Type: application/json

{
  "nome": "Maria Santos",
  "documento": "123.456.789-00"
}
```

## Endpoints de Ocorrências

### Listar Ocorrências
```http
GET /ocorrencias/?skip=0&limit=100
```

### Criar Ocorrência
```http
POST /ocorrencias/
Content-Type: application/json

{
  "numero_genesis": "2024001234",
  "unidade_fato": "Centro",
  "data_apreensao": "2024-08-21",
  "lei_infringida": "Lei 11.343/06",
  "artigo": "Art. 28",
  "policial_condutor_id": 1
}
```

## Endpoints de Itens Apreendidos

### Listar Itens
```http
GET /itens/?skip=0&limit=100
```

### Criar Item
```http
POST /itens/
Content-Type: application/json

{
  "especie": "Entorpecente",
  "item": "Maconha",
  "quantidade": 1,
  "descricao_detalhada": "Pequena porção de substância análoga à maconha",
  "ocorrencia_id": 1,
  "proprietario_id": 1,
  "policial_id": 1
}
```

### Listar Itens por Ocorrência
```http
GET /itens/ocorrencia/{ocorrencia_id}
```

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Erro de validação |
| 404 | Recurso não encontrado |
| 422 | Erro de validação Pydantic |
| 500 | Erro interno do servidor |

## Exemplos de Uso

### Python (requests)
```python
import requests

# Listar policiais
response = requests.get('http://127.0.0.1:8000/policiais/')
policiais = response.json()

# Criar policial
novo_policial = {
    "nome": "Ana Costa",
    "matricula": "54321",
    "graduacao": "Sargento",
    "unidade": "10ª CPR"
}
response = requests.post('http://127.0.0.1:8000/policiais/', json=novo_policial)
```

### JavaScript (fetch)
```javascript
// Listar ocorrências
fetch('http://127.0.0.1:8000/ocorrencias/')
  .then(response => response.json())
  .then(data => console.log(data));

// Criar proprietário
const novoProprietario = {
  nome: "Carlos Oliveira",
  documento: "987.654.321-00"
};

fetch('http://127.0.0.1:8000/proprietarios/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(novoProprietario)
})
.then(response => response.json())
.then(data => console.log(data));
```

### cURL
```bash
# Obter estatísticas
curl -X GET "http://127.0.0.1:8000/estatisticas/"

# Criar item apreendido
curl -X POST "http://127.0.0.1:8000/itens/" \
  -H "Content-Type: application/json" \
  -d '{
    "especie": "Arma",
    "item": "Revólver",
    "quantidade": 1,
    "descricao_detalhada": "Revólver calibre .38",
    "ocorrencia_id": 1,
    "proprietario_id": 1,
    "policial_id": 1
  }'
```

## Documentação Interativa

A API fornece documentação interativa através do Swagger UI:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

## Modelos de Dados

### Policial
```json
{
  "id": 1,
  "nome": "string",
  "matricula": "string",
  "graduacao": "string",
  "unidade": "string"
}
```

### Proprietário
```json
{
  "id": 1,
  "nome": "string",
  "documento": "string"
}
```

### Ocorrência
```json
{
  "id": 1,
  "numero_genesis": "string",
  "unidade_fato": "string",
  "data_apreensao": "2024-08-21",
  "lei_infringida": "string",
  "artigo": "string",
  "policial_condutor_id": 1
}
```

### Item Apreendido
```json
{
  "id": 1,
  "especie": "string",
  "item": "string",
  "quantidade": 1,
  "descricao_detalhada": "string",
  "ocorrencia_id": 1,
  "proprietario_id": 1,
  "policial_id": 1
}
```

## Validações

### Policial
- `matricula`: Deve ser alfanumérica e única
- `nome`: Obrigatório
- `graduacao`: Obrigatório
- `unidade`: Obrigatório

### Proprietário
- `documento`: Mínimo 5 caracteres
- `nome`: Obrigatório

### Item Apreendido
- `quantidade`: Deve ser maior que zero
- Todas as referências (ocorrencia_id, proprietario_id, policial_id) devem existir

## Tratamento de Erros

### Erro de Validação (400)
```json
{
  "detail": "Matrícula já existe"
}
```

### Erro de Validação Pydantic (422)
```json
{
  "detail": [
    {
      "loc": ["body", "quantidade"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

### Recurso Não Encontrado (404)
```json
{
  "detail": "Policial não encontrado"
}
```

## Performance e Limitações

### Paginação
- Parâmetros: `skip` (offset) e `limit` (máximo por página)
- Limite padrão: 100 registros por página
- Limite máximo: 1000 registros por página

### Rate Limiting
Atualmente não implementado. Para produção, considere:
- Limite de requisições por IP
- Limite de requisições por usuário
- Throttling para operações pesadas

### Cache
- Não implementado atualmente
- Considere Redis para cache de consultas frequentes
- Cache de estatísticas pode melhorar performance

## Monitoramento

### Logs
A API gera logs em:
- Console (desenvolvimento)
- Arquivo `secrimpo_server.log` (produção)

### Métricas
Para monitoramento em produção, considere:
- Prometheus + Grafana
- New Relic
- DataDog

## Segurança

### Recomendações para Produção
1. **HTTPS**: Use certificados SSL/TLS
2. **CORS**: Configure origens permitidas
3. **Autenticação**: Implemente JWT ou similar
4. **Rate Limiting**: Previna abuso da API
5. **Validação**: Sanitize todas as entradas
6. **Logs**: Monitore tentativas de acesso

### Headers de Segurança
```python
# Adicionar ao FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
app.add_middleware(HTTPSRedirectMiddleware)  # Apenas em produção
```

---

**Última atualização:** 21/08/2024  
**Versão da API:** 1.0.0  
**FastAPI Version:** 0.104.1+