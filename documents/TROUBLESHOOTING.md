# SECRIMPO - Guia de Solução de Problemas

Soluções para problemas comuns encontrados no uso do SECRIMPO.

## Problemas de Instalação

### Python não encontrado
**Erro:** `'python' is not recognized as an internal or external command`

**Solução:**
```bash
# Verificar se Python está instalado
python --version

# Se não estiver, baixar de python.org
# Ou instalar via chocolatey (Windows)
choco install python

# Ou via apt (Linux)
sudo apt install python3 python3-pip
```

### Node.js não encontrado
**Erro:** `'npm' is not recognized as an internal or external command`

**Solução:**
```bash
# Baixar Node.js de nodejs.org
# Ou instalar via chocolatey (Windows)
choco install nodejs

# Ou via apt (Linux)
sudo apt install nodejs npm
```

### Dependências não instalam
**Erro:** `pip install failed` ou `npm install failed`

**Solução:**
```bash
# Limpar cache do pip
pip cache purge
pip install -r requirements.txt --no-cache-dir

# Limpar cache do npm
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## Problemas da API

### Porta 8000 já está em uso
**Erro:** `[Errno 10048] Only one usage of each socket address`

**Solução:**
```bash
# Windows - Encontrar processo usando porta 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Linux - Encontrar e matar processo
sudo lsof -i :8000
sudo kill -9 <PID>

# Ou usar porta diferente
uvicorn app:app --host 127.0.0.1 --port 8001
```

### API não responde
**Sintomas:** Frontend não conecta, timeout nas requisições

**Diagnóstico:**
```bash
# Testar se API está rodando
curl http://127.0.0.1:8000/

# Verificar logs da API
# Procurar por erros no terminal onde rodou start_api.py
```

**Soluções:**
1. **Reiniciar API:**
   ```bash
   # Parar API (Ctrl+C)
   # Reiniciar
   cd backend && python start_api.py
   ```

2. **Verificar firewall:**
   ```bash
   # Windows
   netsh advfirewall firewall add rule name="SECRIMPO" dir=in action=allow protocol=TCP localport=8000
   
   # Linux
   sudo ufw allow 8000
   ```

3. **Verificar antivírus:**
   - Adicionar exceção para pasta do SECRIMPO
   - Temporariamente desabilitar proteção em tempo real

### Banco de dados corrompido
**Erro:** `database disk image is malformed`

**Solução:**
```bash
# Backup do banco atual
copy backend\secrimpo.db backend\secrimpo_corrupted.db

# Tentar reparar
sqlite3 backend\secrimpo.db ".recover" | sqlite3 backend\secrimpo_repaired.db

# Se não funcionar, criar novo banco
del backend\secrimpo.db
cd backend && python start_api.py
```

### Erro de importação de módulos
**Erro:** `ModuleNotFoundError: No module named 'fastapi'`

**Solução:**
```bash
# Verificar se está no ambiente virtual correto
which python
pip list | grep fastapi

# Reinstalar dependências
pip install -r requirements.txt

# Se persistir, usar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux
pip install -r requirements.txt
```

## Problemas do Frontend

### Electron não abre
**Sintomas:** Comando `npm start` executa mas janela não abre

**Solução:**
```bash
# Verificar se há erros no console
npm start

# Limpar cache do Electron
npm run clean
rm -rf node_modules
npm install

# Executar em modo debug
npm run dev
```

### Tela branca no Electron
**Sintomas:** Janela abre mas mostra tela branca

**Diagnóstico:**
1. Abrir DevTools: F12 ou Ctrl+Shift+I
2. Verificar erros no Console
3. Verificar se arquivos estão carregando na aba Network

**Soluções:**
1. **Problema de CORS:**
   ```javascript
   // Verificar se API_BASE está correto em app.js
   const API_BASE = "http://127.0.0.1:8000";
   ```

2. **Arquivos não encontrados:**
   ```bash
   # Verificar se arquivos existem
   ls frontend/src/
   
   # Verificar se paths estão corretos em index.html
   ```

3. **Erro de JavaScript:**
   - Verificar console do DevTools
   - Corrigir erros de sintaxe
   - Verificar se Font Awesome está carregando

### Frontend não conecta com API
**Sintomas:** Mensagens de erro "Não foi possível conectar à API"

**Diagnóstico:**
```bash
# Testar API manualmente
curl http://127.0.0.1:8000/

# Verificar se API está rodando
netstat -an | findstr :8000
```

**Soluções:**
1. **API não está rodando:**
   ```bash
   cd backend
   python start_api.py
   ```

2. **URL incorreta:**
   ```javascript
   // Verificar em frontend/src/app.js
   const API_BASE = "http://127.0.0.1:8000";  // Deve estar correto
   ```

3. **Problema de CORS:**
   ```python
   # Verificar em backend/app.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Deve permitir origem do frontend
   )
   ```

### Formulário não salva
**Sintomas:** Clica em "Salvar" mas nada acontece

**Diagnóstico:**
1. Abrir DevTools (F12)
2. Verificar Console por erros
3. Verificar Network por requisições falhando

**Soluções:**
1. **Campos obrigatórios:**
   - Verificar se todos os campos obrigatórios estão preenchidos
   - Campos em vermelho indicam erro

2. **Validação de documentos:**
   - CPF deve estar válido (indicador verde)
   - RG deve ter formato correto

3. **Erro de rede:**
   ```javascript
   // Verificar se API está respondendo
   fetch('http://127.0.0.1:8000/')
     .then(r => r.json())
     .then(console.log)
     .catch(console.error);
   ```

## Problemas de Rede (Multi-usuário)

### Pasta compartilhada não acessível
**Erro:** `\\servidor\pasta não foi encontrado`

**Solução:**
```bash
# Verificar conectividade
ping servidor

# Testar acesso manual
\\servidor\pasta

# Verificar credenciais
net use \\servidor\pasta /user:DOMAIN\usuario

# Mapear unidade
net use Z: \\servidor\pasta /persistent:yes
```

### Múltiplos usuários travando banco
**Sintomas:** "Database is locked" ou timeouts frequentes

**Solução:**
1. **Configurar WAL mode:**
   ```python
   # Executar script setup_wal.py
   python backend/setup_wal.py
   ```

2. **Reduzir concorrência:**
   - Limitar número de usuários simultâneos
   - Implementar retry automático

3. **Migrar para Master-Slave:**
   - Seguir guia em NETWORK_SYNC_GUIDE.md
   - Um PC como servidor, outros como clientes

### PC servidor não acessível
**Sintomas:** Clientes não conseguem conectar ao servidor

**Diagnóstico:**
```bash
# Do cliente, testar conectividade
ping 192.168.1.100
telnet 192.168.1.100 8000

# Do servidor, verificar se API está ouvindo
netstat -an | findstr :8000
```

**Soluções:**
1. **Firewall bloqueando:**
   ```bash
   # Windows
   netsh advfirewall firewall add rule name="SECRIMPO" dir=in action=allow protocol=TCP localport=8000
   
   # Linux
   sudo ufw allow 8000
   ```

2. **API ouvindo apenas localhost:**
   ```python
   # Verificar em start_api.py
   uvicorn.run("app:app", host="0.0.0.0", port=8000)  # Não 127.0.0.1
   ```

3. **IP do servidor mudou:**
   - Configurar IP fixo no servidor
   - Atualizar configuração nos clientes

## Problemas de Performance

### Sistema lento
**Sintomas:** Interface travando, operações demoradas

**Diagnóstico:**
```bash
# Verificar uso de recursos
# Windows
tasklist | findstr python
tasklist | findstr electron

# Linux
ps aux | grep python
ps aux | grep electron
```

**Soluções:**
1. **Banco de dados grande:**
   ```sql
   -- Verificar tamanho das tabelas
   SELECT name, COUNT(*) FROM sqlite_master sm, pragma_table_info(sm.name) GROUP BY name;
   
   -- Limpar dados antigos se necessário
   DELETE FROM ocorrencia WHERE data_apreensao < '2023-01-01';
   ```

2. **Muitos registros sendo carregados:**
   ```javascript
   // Implementar paginação no frontend
   const response = await fetch(`${API_BASE}/policiais/?limit=50`);
   ```

3. **Rede lenta (modo compartilhado):**
   - Migrar para modo Master-Slave
   - Usar SSD no servidor
   - Melhorar infraestrutura de rede

### Memória insuficiente
**Sintomas:** Sistema trava, erro "Out of memory"

**Solução:**
```bash
# Verificar uso de memória
# Windows
tasklist /fi "imagename eq python.exe"

# Linux
ps aux | grep python | awk '{print $6}'

# Reiniciar aplicação periodicamente
# Implementar limpeza de cache
```

## Problemas de Dados

### Dados duplicados
**Sintomas:** Mesmo policial/proprietário aparece múltiplas vezes

**Solução:**
```sql
-- Encontrar duplicatas
SELECT matricula, COUNT(*) FROM policial GROUP BY matricula HAVING COUNT(*) > 1;

-- Remover duplicatas (manter apenas o primeiro)
DELETE FROM policial WHERE id NOT IN (
    SELECT MIN(id) FROM policial GROUP BY matricula
);
```

### Dados inconsistentes
**Sintomas:** Referências quebradas, itens sem proprietário

**Diagnóstico:**
```sql
-- Verificar integridade referencial
SELECT * FROM item_apreendido WHERE policial_id NOT IN (SELECT id FROM policial);
SELECT * FROM item_apreendido WHERE proprietario_id NOT IN (SELECT id FROM proprietario);
SELECT * FROM item_apreendido WHERE ocorrencia_id NOT IN (SELECT id FROM ocorrencia);
```

**Solução:**
```sql
-- Corrigir referências quebradas
DELETE FROM item_apreendido WHERE policial_id NOT IN (SELECT id FROM policial);
-- Ou criar registros faltantes conforme necessário
```

### Backup e Recuperação
**Problema:** Perda de dados

**Prevenção:**
```bash
# Backup automático diário
# Windows (Task Scheduler)
copy "C:\SECRIMPO\backend\secrimpo.db" "C:\Backup\secrimpo_%date%.db"

# Linux (crontab)
0 2 * * * cp /path/to/secrimpo.db /backup/secrimpo_$(date +\%Y\%m\%d).db
```

**Recuperação:**
```bash
# Restaurar backup
copy "C:\Backup\secrimpo_20240821.db" "C:\SECRIMPO\backend\secrimpo.db"

# Verificar integridade
sqlite3 backend/secrimpo.db "PRAGMA integrity_check;"
```

## Scripts de Diagnóstico

### Script de Diagnóstico Completo
```python
#!/usr/bin/env python3
"""
Script de diagnóstico completo do SECRIMPO
"""
import os
import sys
import sqlite3
import requests
import psutil
from pathlib import Path

def diagnose_system():
    print("=== DIAGNÓSTICO SECRIMPO ===\n")
    
    # 1. Verificar Python
    print(f"Python: {sys.version}")
    
    # 2. Verificar dependências
    try:
        import fastapi, sqlalchemy, pandas
        print("✓ Dependências Python OK")
    except ImportError as e:
        print(f"✗ Dependência faltando: {e}")
    
    # 3. Verificar arquivos
    files = [
        "backend/app.py",
        "backend/secrimpo.db",
        "frontend/src/index.html",
        "frontend/package.json"
    ]
    
    for file in files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} não encontrado")
    
    # 4. Verificar API
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✓ API respondendo: {response.status_code}")
    except:
        print("✗ API não está respondendo")
    
    # 5. Verificar banco
    try:
        conn = sqlite3.connect("backend/secrimpo.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchone()[0]
        print(f"✓ Banco OK: {tables} tabelas")
        conn.close()
    except Exception as e:
        print(f"✗ Erro no banco: {e}")
    
    # 6. Verificar recursos
    print(f"CPU: {psutil.cpu_percent()}%")
    print(f"RAM: {psutil.virtual_memory().percent}%")
    print(f"Disco: {psutil.disk_usage('.').percent}%")

if __name__ == "__main__":
    diagnose_system()
```

## Contato para Suporte

### Informações para Incluir no Reporte
1. **Sistema Operacional:** Windows/Linux + versão
2. **Versão do Python:** `python --version`
3. **Versão do Node.js:** `node --version`
4. **Erro específico:** Mensagem completa de erro
5. **Logs:** Console da API e frontend
6. **Passos para reproduzir:** O que estava fazendo quando o erro ocorreu

### Canais de Suporte
- **GitHub Issues:** Para bugs e problemas técnicos
- **Documentação:** Consulte outros arquivos em `/documents/`
- **FAQ:** Perguntas frequentes em `FAQ.md`

---

**Última atualização:** 21/08/2024  
**Versão:** 1.0.0  
**Compatibilidade:** SECRIMPO v1.0.0+