/**
 * Exemplo de integração da sincronização no app principal SECRIMPO
 * Este arquivo mostra como integrar o SyncManager no seu app Electron existente
 */

// === EXEMPLO DE INTEGRAÇÃO NO HTML PRINCIPAL ===

/*
Adicione este HTML no seu index.html principal:

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
*/

// === CLASSE DE INTEGRAÇÃO ===

class SyncAppIntegration {
    constructor() {
        this.syncManager = window.syncManager;
        this.isInitialized = false;
        
        // Aguardar DOM carregar
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }
    
    initialize() {
        if (this.isInitialized) return;
        
        console.log('Inicializando integração de sincronização...');
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Carregar usuário salvo
        this.loadSavedUser();
        
        // Verificar se precisa sincronizar automaticamente
        this.checkAutoSync();
        
        // Atualizar interface periodicamente
        setInterval(() => this.updateUI(), 10000);
        
        this.isInitialized = true;
        console.log('Integração de sincronização inicializada');
    }
    
    setupEventListeners() {
        // Botão de usuário
        const userInput = document.getElementById('usuario-sync');
        if (userInput) {
            userInput.addEventListener('change', (e) => {
                const usuario = e.target.value.trim();
                if (usuario) {
                    this.syncManager.setUsuario(usuario);
                    this.updateUI();
                }
            });
        }
        
        // Escutar mudanças de conectividade
        window.addEventListener('online', () => {
            console.log('Conexão restaurada');
            this.syncManager.checkConnectivity();
        });
        
        window.addEventListener('offline', () => {
            console.log('Conexão perdida');
            this.syncManager.updateConnectionStatus(false);
        });
    }
    
    loadSavedUser() {
        const usuario = this.syncManager.getUsuario();
        const userInput = document.getElementById('usuario-sync');
        
        if (usuario && userInput) {
            userInput.value = usuario;
        }
    }
    
    async checkAutoSync() {
        // Verificar se precisa sincronizar (mais de 24h desde a última)
        if (this.syncManager.needsSync(24)) {
            const usuario = this.syncManager.getUsuario();
            
            if (usuario && this.syncManager.isOnline) {
                // Mostrar notificação perguntando se quer sincronizar
                this.showSyncNotification();
            }
        }
    }
    
    showSyncNotification() {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 300px;
        `;
        
        notification.innerHTML = `
            <div style="margin-bottom: 10px;">
                <strong>🔄 Sincronização Recomendada</strong>
            </div>
            <div style="margin-bottom: 15px; font-size: 14px;">
                Há mais de 24h desde a última sincronização. Deseja sincronizar agora?
            </div>
            <div>
                <button onclick="syncApp.executarSincronizacao(); this.parentElement.parentElement.remove();" 
                        style="background: #007bff; color: white; border: none; padding: 5px 10px; border-radius: 3px; margin-right: 5px; cursor: pointer;">
                    Sim
                </button>
                <button onclick="this.parentElement.parentElement.remove();" 
                        style="background: #6c757d; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                    Depois
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remover automaticamente após 10 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 10000);
    }
    
    async executarSincronizacao() {
        const usuario = this.syncManager.getUsuario();
        
        if (!usuario) {
            alert('Por favor, defina seu nome/ID de usuário antes de sincronizar.');
            const userInput = document.getElementById('usuario-sync');
            if (userInput) userInput.focus();
            return;
        }
        
        if (!this.syncManager.isOnline) {
            alert('Sem conexão com o servidor. Verifique se a API está rodando.');
            return;
        }
        
        try {
            console.log('Iniciando sincronização...');
            
            // Mostrar indicador de carregamento
            const syncButton = document.getElementById('sync-button');
            const originalText = syncButton ? syncButton.textContent : '';
            if (syncButton) {
                syncButton.textContent = '⏳ Sincronizando...';
                syncButton.disabled = true;
            }
            
            const resultado = await this.syncManager.sincronizar(true);
            
            if (resultado.sucesso) {
                console.log('Sincronização concluída:', resultado.message);
                this.showToast(resultado.message, 'success');
                
                // Atualizar dados locais se necessário
                this.onSyncSuccess(resultado);
            } else {
                console.error('Falha na sincronização');
                this.showToast('Falha na sincronização. Verifique a conexão.', 'error');
            }
            
        } catch (error) {
            console.error('Erro durante sincronização:', error);
            this.showToast(`Erro: ${error.message}`, 'error');
        } finally {
            // Restaurar botão
            const syncButton = document.getElementById('sync-button');
            if (syncButton) {
                syncButton.textContent = originalText || '🔄 Sincronizar';
                syncButton.disabled = !this.syncManager.isOnline;
            }
            
            this.updateUI();
        }
    }
    
    onSyncSuccess(resultado) {
        // Callback chamado após sincronização bem-sucedida
        // Aqui você pode atualizar a interface, recarregar dados, etc.
        
        console.log('Sincronização bem-sucedida:', resultado.resumo);
        
        // Exemplo: recarregar lista de ocorrências se houver novas
        if (resultado.resumo.ocorrencias && resultado.resumo.ocorrencias.novos > 0) {
            // Recarregar dados na interface
            if (typeof window.reloadOcorrencias === 'function') {
                window.reloadOcorrencias();
            }
        }
        
        // Exemplo: recarregar lista de policiais se houver novos
        if (resultado.resumo.policiais && resultado.resumo.policiais.novos > 0) {
            if (typeof window.reloadPoliciais === 'function') {
                window.reloadPoliciais();
            }
        }
    }
    
    updateUI() {
        // Atualizar status de conexão
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = this.syncManager.isOnline ? '🟢 Online' : '🔴 Offline';
            statusElement.title = this.syncManager.isOnline ? 
                'Conectado ao servidor central' : 
                'Sem conexão com servidor';
        }
        
        // Atualizar botão de sincronização
        const syncButton = document.getElementById('sync-button');
        if (syncButton) {
            syncButton.disabled = !this.syncManager.isOnline;
        }
        
        // Atualizar informações da última sincronização
        this.updateLastSyncInfo();
    }
    
    updateLastSyncInfo() {
        const lastSyncElement = document.getElementById('last-sync-info');
        if (!lastSyncElement) return;
        
        const lastSync = this.syncManager.getLastSyncInfo();
        if (lastSync) {
            const agora = new Date();
            const diffMinutos = Math.floor((agora - lastSync) / (1000 * 60));
            
            let texto = '';
            if (diffMinutos < 1) {
                texto = 'Sincronizado agora';
            } else if (diffMinutos < 60) {
                texto = `Sincronizado há ${diffMinutos}min`;
            } else if (diffMinutos < 1440) {
                texto = `Sincronizado há ${Math.floor(diffMinutos / 60)}h`;
            } else {
                texto = `Sincronizado há ${Math.floor(diffMinutos / 1440)}d`;
            }
            
            lastSyncElement.textContent = texto;
        } else {
            lastSyncElement.textContent = 'Nunca sincronizado';
        }
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            max-width: 300px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        `;
        
        switch (type) {
            case 'success':
                toast.style.background = '#28a745';
                break;
            case 'error':
                toast.style.background = '#dc3545';
                break;
            case 'warning':
                toast.style.background = '#ffc107';
                toast.style.color = '#212529';
                break;
            default:
                toast.style.background = '#17a2b8';
        }
        
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // Remover após 4 segundos
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 4000);
    }
    
    abrirTelaSincronizacao() {
        // Abrir tela de configuração de sincronização
        const { shell } = require('electron');
        const path = require('path');
        
        // Abrir arquivo HTML de sincronização
        const syncHtmlPath = path.join(__dirname, 'sync-ui.html');
        shell.openPath(syncHtmlPath);
    }
    
    // Método para ser chamado quando novos dados são criados localmente
    onDataCreated(tipo, dados) {
        console.log(`Novos dados criados: ${tipo}`, dados);
        
        // Adicionar UUID se não existir
        if (!dados.uuid_local) {
            dados.uuid_local = this.syncManager.generateUuid();
            
            // Salvar UUID no banco local
            if (typeof window.dbManager !== 'undefined') {
                window.dbManager.updateRecordUuid(tipo, dados.id, dados.uuid_local);
            }
        }
        
        // Sugerir sincronização se online
        if (this.syncManager.isOnline) {
            this.showToast('Dados salvos localmente. Considere sincronizar.', 'info');
        }
    }
    
    // Método para verificar se há dados não sincronizados
    async checkUnsyncedData() {
        try {
            if (typeof window.dbManager !== 'undefined') {
                const unsyncedCount = await window.dbManager.getUnsyncedCount();
                
                if (unsyncedCount > 0) {
                    const message = `Você tem ${unsyncedCount} registros não sincronizados.`;
                    this.showToast(message, 'warning');
                    return unsyncedCount;
                }
            }
        } catch (error) {
            console.error('Erro ao verificar dados não sincronizados:', error);
        }
        
        return 0;
    }
}

// === EXEMPLO DE USO NO DATABASE MANAGER ===

/*
// Adicione estas funções ao seu database manager existente:

// Função para adicionar UUID aos registros
async function addUuidToRecord(tableName, recordId) {
    const uuid = generateUuid();
    const query = `UPDATE ${tableName} SET uuid_local = ? WHERE id = ?`;
    await db.run(query, [uuid, recordId]);
    return uuid;
}

// Função para obter registros não sincronizados
async function getUnsyncedCount() {
    const tables = ['policial', 'proprietario', 'ocorrencia'];
    let total = 0;
    
    for (const table of tables) {
        const result = await db.get(`
            SELECT COUNT(*) as count 
            FROM ${table} 
            WHERE uuid_local IS NULL OR uuid_local = ''
        `);
        total += result.count;
    }
    
    return total;
}

// Função para obter todos os dados com relacionamentos para sincronização
async function getAllOcorrenciasCompletas() {
    const query = `
        SELECT 
            o.*,
            p.nome as policial_nome,
            p.matricula as policial_matricula,
            p.graduacao as policial_graduacao,
            p.unidade as policial_unidade
        FROM ocorrencia o
        JOIN policial p ON o.policial_condutor_id = p.id
    `;
    
    const ocorrencias = await db.all(query);
    
    // Buscar itens para cada ocorrência
    for (const ocorrencia of ocorrencias) {
        const itens = await db.all(`
            SELECT 
                i.*,
                pr.nome as proprietario_nome,
                pr.documento as proprietario_documento
            FROM item_apreendido i
            JOIN proprietario pr ON i.proprietario_id = pr.id
            WHERE i.ocorrencia_id = ?
        `, [ocorrencia.id]);
        
        ocorrencia.itens_apreendidos = itens.map(item => ({
            especie: item.especie,
            item: item.item,
            quantidade: item.quantidade,
            descricao_detalhada: item.descricao_detalhada,
            proprietario: {
                nome: item.proprietario_nome,
                documento: item.proprietario_documento
            }
        }));
        
        ocorrencia.policial_condutor = {
            nome: ocorrencia.policial_nome,
            matricula: ocorrencia.policial_matricula,
            graduacao: ocorrencia.policial_graduacao,
            unidade: ocorrencia.policial_unidade
        };
    }
    
    return ocorrencias;
}
*/

// Instância global
window.syncApp = new SyncAppIntegration();

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SyncAppIntegration;
}