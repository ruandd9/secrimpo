# 🗂️ SECRIMPO - Guia da Pasta Compartilhada

Guia prático para configurar e usar uma pasta compartilhada onde múltiplos usuários podem inserir e acessar dados do SECRIMPO simultaneamente.

## 🎯 O que é a Pasta Compartilhada?

A pasta compartilhada permite que vários usuários em diferentes computadores:
- **Vejam os mesmos dados** em tempo real
- **Insiram ocorrências** que aparecem para todos
- **Façam backup centralizado** em um só local
- **Trabalhem simultaneamente** sem conflitos

## 🚀 Configuração Rápida (5 minutos)

### 1. Execute o Configurador
```bash
python setup_shared_folder.py
```

### 2. Escolha uma Opção
- **Opção 1**: Pasta local compartilhada (mais simples)
- **Opção 2**: Servidor de arquivos (mais robusto)
- **Opção 3**: Unidade mapeada (mais conveniente)
- **Opção 4**: Detectar automaticamente

### 3. Teste a Configuração
```bash
python test_shared_setup.py
```

### 4. Inicie o SECRIMPO
```bash
python backend/start_api.py
```

## 📋 Cenários de Uso

### Cenário 1: Escritório Pequeno (2-5 PCs)

**Situação**: Escritório com poucos computadores na mesma rede local.

**Solução Recomendada**: Pasta Local Compartilhada

**Configuração**:
1. Escolha um PC como "servidor" (pode ser qualquer um)
2. Execute `python setup_shared_folder.py`
3. Escolha opção 1 (Pasta Local)
4. Compartilhe a pasta criada via Windows/Linux
5. Nos outros PCs, execute o mesmo script
6. Aponte para a pasta compartilhada: `\\pc-servidor\SecrimpoShared`

**Vantagens**:
- ✅ Configuração simples
- ✅ Sem necessidade de servidor dedicado
- ✅ Funciona com infraestrutura existente

### Cenário 2: Escritório com Servidor (5+ PCs)

**Situação**: Escritório com servidor de arquivos existente.

**Solução Recomendada**: Servidor de Arquivos

**Configuração**:
1. Crie pasta no servidor: `\\servidor\SecrimpoData`
2. Configure permissões para todos os usuários
3. Em cada PC, execute `python setup_shared_folder.py`
4. Escolha opção 2 (Pasta de Rede)
5. Digite: `\\servidor\SecrimpoData`

**Vantagens**:
- ✅ Melhor performance
- ✅ Backup centralizado profissional
- ✅ Suporta mais usuários simultâneos

### Cenário 3: Unidade Mapeada

**Situação**: Já existe unidade de rede mapeada (ex: Z:)

**Solução Recomendada**: Unidade Mapeada

**Configuração**:
1. Certifique-se que todos têm a mesma unidade mapeada
2. Execute `python setup_shared_folder.py`
3. Escolha opção 3 (Unidade Mapeada)
4. Digite: `Z:\SecrimpoData`

**Vantagens**:
- ✅ Transparente para usuários
- ✅ Fácil de lembrar o caminho
- ✅ Integração com sistema existente

## 🔧 Configuração Detalhada

### Passo 1: Preparar a Pasta Compartilhada

#### Windows (Compartilhamento SMB)
```cmd
# Criar pasta
mkdir C:\SecrimpoShared

# Compartilhar via interface gráfica:
# 1. Clique direito na pasta
# 2. Propriedades > Compartilhamento
# 3. Compartilhamento Avançado
# 4. Marque "Compartilhar esta pasta"
# 5. Permissões > Adicionar "Todos" com "Controle Total"

# Ou via linha de comando:
net share SecrimpoShared=C:\SecrimpoShared /grant:everyone,full
```

#### Linux (Samba)
```bash
# Instalar Samba
sudo apt install samba

# Criar pasta
sudo mkdir /srv/secrimpo
sudo chmod 777 /srv/secrimpo

# Configurar Samba (/etc/samba/smb.conf)
[secrimpo]
path = /srv/secrimpo
browseable = yes
writable = yes
guest ok = yes
create mask = 0777
directory mask = 0777

# Reiniciar Samba
sudo systemctl restart smbd
```

### Passo 2: Configurar Cada PC Cliente

Em cada computador que usará o SECRIMPO:

```bash
# 1. Baixar/clonar o projeto SECRIMPO
git clone <url-do-repositorio>
cd secrimpo

# 2. Instalar dependências
pip install -r backend/requirements.txt

# 3. Configurar pasta compartilhada
python setup_shared_folder.py

# 4. Testar configuração
python test_shared_setup.py

# 5. Iniciar SECRIMPO
python backend/start_api.py
```

### Passo 3: Verificar Funcionamento

#### Teste de Sincronização
1. **PC 1**: Crie uma ocorrência
2. **PC 2**: Verifique se a ocorrência aparece
3. **PC 3**: Edite dados de um policial
4. **PC 1**: Confirme que as mudanças aparecem

#### Teste de Performance
```bash
# Execute em cada PC
python backend/diagnostico_compartilhado.py
```

## 🛠️ Solução de Problemas

### Problema: "Pasta compartilhada não acessível"

**Possíveis Causas**:
- Pasta não existe
- Sem permissões de acesso
- Problemas de rede
- Firewall bloqueando

**Soluções**:
```bash
# Verificar se pasta existe
dir \\servidor\SecrimpoData

# Testar conectividade
ping servidor

# Verificar permissões
# Windows: Propriedades > Segurança
# Linux: ls -la /srv/secrimpo

# Mapear unidade temporariamente
net use Z: \\servidor\SecrimpoData
```

### Problema: "Banco de dados corrompido"

**Sintomas**:
- Erros ao salvar dados
- Dados não aparecem
- API não inicia

**Soluções**:
```bash
# Verificar integridade
python backend/diagnostico_compartilhado.py

# Restaurar backup
# Os backups ficam em: pasta_compartilhada/backups/
copy "pasta_compartilhada\backups\secrimpo_backup_YYYYMMDD.db" "pasta_compartilhada\database\secrimpo.db"

# Recriar banco (PERDE DADOS!)
del "pasta_compartilhada\database\secrimpo.db"
python backend/shared_storage.py
```

### Problema: "Performance lenta"

**Sintomas**:
- Sistema demora para responder
- Salvamento lento
- Interface trava

**Soluções**:
```bash
# Verificar performance
python backend/diagnostico_compartilhado.py

# Otimizações de rede:
# 1. Usar cabo ethernet em vez de WiFi
# 2. Verificar se outros programas estão usando rede
# 3. Considerar SSD no servidor
# 4. Aumentar cache do SQLite (automático)
```

### Problema: "Múltiplos usuários conflitando"

**Sintomas**:
- Dados não salvam
- Erro "database is locked"
- Inconsistências nos dados

**Soluções**:
- ✅ Sistema usa WAL mode (automático)
- ✅ Timeout configurado para 30 segundos
- ✅ Máximo 10 usuários simultâneos recomendado
- ⚠️ Se persistir, considere modo Master-Slave

## 📊 Monitoramento e Manutenção

### Verificação Diária
```bash
# Status rápido
python test_shared_setup.py

# Diagnóstico completo (semanal)
python backend/diagnostico_compartilhado.py
```

### Backup Automático
O sistema cria backups automaticamente em:
- `pasta_compartilhada/backups/`
- Backup diário automático
- Manter últimos 30 backups

### Logs do Sistema
Verifique logs em caso de problemas:
- `pasta_compartilhada/logs/`
- Logs de diagnóstico
- Logs de erro da aplicação

## 📈 Escalabilidade

### Até 5 usuários
- ✅ Pasta compartilhada funciona perfeitamente
- ✅ Performance excelente
- ✅ Configuração simples

### 5-10 usuários
- ✅ Pasta compartilhada ainda funciona
- ⚠️ Monitorar performance
- ⚠️ Considerar servidor dedicado

### 10+ usuários
- ❌ Pasta compartilhada pode ter limitações
- ✅ Migrar para modo Master-Slave
- ✅ Considerar PostgreSQL/MySQL

## 🎉 Resumo dos Benefícios

### Para Usuários
- 👥 **Colaboração**: Todos veem os mesmos dados
- 🔄 **Sincronização**: Automática e em tempo real
- 💾 **Backup**: Centralizado e automático
- 🚀 **Facilidade**: Configuração em 5 minutos

### Para Administradores
- 🛠️ **Manutenção**: Um só local para gerenciar
- 📊 **Monitoramento**: Ferramentas de diagnóstico
- 🔒 **Segurança**: Controle de acesso centralizado
- 💰 **Custo**: Sem necessidade de servidor dedicado

## 📞 Suporte

### Documentação Adicional
- [NETWORK_SYNC_GUIDE.md](documents/NETWORK_SYNC_GUIDE.md) - Guia técnico completo
- [TROUBLESHOOTING.md](documents/TROUBLESHOOTING.md) - Solução de problemas
- [API_DOCUMENTATION.md](documents/API_DOCUMENTATION.md) - Documentação da API

### Scripts Úteis
- `setup_shared_folder.py` - Configurador principal
- `test_shared_setup.py` - Teste de configuração
- `backend/diagnostico_compartilhado.py` - Diagnóstico completo
- `backend/shared_storage.py` - Gerenciador de armazenamento

### Comandos de Emergência
```bash
# Reconfigurar tudo
python setup_shared_folder.py

# Diagnóstico completo
python backend/diagnostico_compartilhado.py

# Restaurar backup
# Vá para pasta_compartilhada/backups/ e copie o backup mais recente
```

---

**🎯 Objetivo**: Permitir que múltiplos usuários trabalhem com os mesmos dados do SECRIMPO de forma simples e eficiente.

**⏱️ Tempo de configuração**: 5-10 minutos por PC

**👥 Usuários suportados**: Até 10 simultâneos

**🔧 Manutenção**: Mínima, com ferramentas automatizadas