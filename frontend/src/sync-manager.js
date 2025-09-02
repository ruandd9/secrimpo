/**
 * Gerenciador de Sincronização - SECRIMPO
 * Responsável por sincronizar dados locais com o servidor central
 */

class SyncManager {
    constructor() {
        this.serverUrl = 'http://10.160.215.16:8001';
        this.clientUuid = this.getOrCreateClientUuid();
        this.usuario = null;
        this.isOnline = false;
        this.lastSyncTime = null;
        
        // Verificar conectividade periodicamente
        this.checkConnectivity();
        setInterval(() => this.checkConnectivity(), 30000); // A cada 30 segundos
    }
    
    /**
     * Gera ou recupera UUID único do cliente
     */
    getOrCreateClientUuid() {
        let uuid = localStorage.getItem('secrimpo_client_uuid');
        if (!uuid) {
            uuid = this.generateUuid();
            localStorage.setItem('secrimpo_client_uuid', uuid);
        }
        return uuid;
    }
    
    /**
     * Gera UUID simples
     */
    generateUuid() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    /**
     * Define o usuário atual
     */
    setUsuario(nomeUsuario) {
        this.usuario = nomeUsuario;
        localStorage.setItem('secrimpo_usuario', nomeUsuario);
    }
    
    /**
     * Obtém o usuário atual
     */
    getUsuario() {
        if (!this.usuario) {
            this.usuario = localStorage.getItem('secrimpo_usuario');
        }
        return this.usuario;
    }
    
    /**
     * Verifica conectividade com o servidor
     */
    async checkConnectivity() {
        try {
            const response = await fetch(`${this.serverUrl}/sincronizar/teste`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 5000
            });
            
            if (response.ok) {
                this.isOnline = true;
                this.updateConnectionStatus(true);
                return true;
            }
        } catch (error) {
            console.log('Servidor offline:', error.message);
        }
        
        this.isOnline = false;
        this.updateConnectionStatus(false);
        return false;
    }
    
    /**
     * Atualiza indicador visual de conectividade
     */
    updateConnectionStatus(online) {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = online ? 'online' : 'offline';
            indicator.textContent = online ? '🟢 Online' : '🔴 Offline';
            indicator.title = online ? 'Conectado ao servidor central' : 'Sem conexão com servidor';
        }
        
        // Habilitar/desabilitar botão de sincronização
        const syncButton = document.getElementById('sync-button');
        if (syncButton) {
            syncButton.disabled = !online;
        }
    }
    
    /**
     * Coleta dados locais para sincronização
     */
    async coletarDadosLocais() {
        const dados = {
            policiais: [],
            proprietarios: [],
            ocorrencias: []
        };
        
        try {
            // Coletar policiais (assumindo que existe uma função global ou API local)
            if (typeof window.dbManager !== 'undefined') {
                dados.policiais = await window.dbManager.getAllPoliciais();
                dados.proprietarios = await window.dbManager.getAllProprietarios();
                dados.ocorrencias = await window.dbManager.getAllOcorrenciasCompletas();
            }
            
            // Adicionar UUIDs se não existirem
            dados.policiais = dados.policiais.map(p => ({
                ...p,
                uuid_local: p.uuid_local || this.generateUuid()
            }));
            
            dados.proprietarios = dados.proprietarios.map(p => ({
                ...p,
                uuid_local: p.uuid_local || this.generateUuid()
            }));
            
            dados.ocorrencias = dados.ocorrencias.map(o => ({
                ...o,
                uuid_local: o.uuid_local || this.generateUuid(),
                data_apreensao: o.data_apreensao // Garantir formato ISO
            }));
            
        } catch (error) {
            console.error('Erro ao coletar dados locais:', error);
            throw new Error('Falha ao coletar dados locais: ' + error.message);
        }
        
        return dados;
    }
    
    /**
     * Executa sincronização completa
     */
    async sincronizar(mostrarProgresso = true) {
        if (!this.isOnline) {
            throw new Error('Sem conexão com o servidor. Verifique sua conexão de rede.');
        }
        
        const usuario = this.getUsuario();
        if (!usuario) {
            throw new Error('Usuário não definido. Configure o usuário antes de sincronizar.');
        }
        
        if (mostrarProgresso) {
            this.showSyncProgress('Coletando dados locais...');
        }
        
        try {
            // Coletar dados locais
            const dados = await this.coletarDadosLocais();
            
            // Verificar se há dados para sincronizar
            const totalRegistros = dados.policiais.length + dados.proprietarios.length + dados.ocorrencias.length;
            if (totalRegistros === 0) {
                if (mostrarProgresso) {
                    this.hideSyncProgress();
                }
                return {
                    sucesso: true,
                    message: 'Nenhum dado para sincronizar',
                    resumo: { total: 0 }
                };
            }
            
            if (mostrarProgresso) {
                this.showSyncProgress(`Enviando ${totalRegistros} registros...`);
            }
            
            // Preparar payload
            const payload = {
                usuario: usuario,
                client_uuid: this.clientUuid,
                timestamp_cliente: new Date().toISOString(),
                dados: dados
            };
            
            // Enviar para servidor
            const response = await fetch(`${this.serverUrl}/sincronizar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Erro HTTP ${response.status}`);
            }
            
            const resultado = await response.json();
            
            if (mostrarProgresso) {
                this.hideSyncProgress();
            }
            
            // Salvar timestamp da última sincronização
            this.lastSyncTime = new Date();
            localStorage.setItem('secrimpo_last_sync', this.lastSyncTime.toISOString());
            
            // Atualizar UUIDs locais se necessário
            await this.atualizarUuidsLocais(dados);
            
            return {
                sucesso: resultado.sucesso,
                message: this.formatarMensagemResultado(resultado),
                resumo: resultado.resumo,
                detalhes: resultado.detalhes,
                erros: resultado.erros
            };
            
        } catch (error) {
            if (mostrarProgresso) {
                this.hideSyncProgress();
            }
            console.error('Erro durante sincronização:', error);
            throw error;
        }
    }
    
    /**
     * Formata mensagem de resultado da sincronização
     */
    formatarMensagemResultado(resultado) {
        const resumo = resultado.resumo || {};
        let totalNovos = 0;
        let totalDuplicados = 0;
        
        Object.values(resumo).forEach(r => {
            totalNovos += r.novos || 0;
            totalDuplicados += r.duplicados || 0;
        });
        
        const total = totalNovos + totalDuplicados;
        
        if (total === 0) {
            return 'Nenhum dado foi sincronizado';
        }
        
        let msg = `Sincronização concluída: ${total} registros processados`;
        if (totalNovos > 0) {
            msg += `, ${totalNovos} novos`;
        }
        if (totalDuplicados > 0) {
            msg += `, ${totalDuplicados} já existiam`;
        }
        
        if (resultado.erros && resultado.erros.length > 0) {
            msg += ` (${resultado.erros.length} erros)`;
        }
        
        return msg;
    }
    
    /**
     * Atualiza UUIDs locais após sincronização
     */
    async atualizarUuidsLocais(dados) {
        try {
            if (typeof window.dbManager !== 'undefined') {
                // Atualizar UUIDs nos registros locais
                for (const policial of dados.policiais) {
                    if (policial.uuid_local) {
                        await window.dbManager.updatePolicialUuid(policial.id, policial.uuid_local);
                    }
                }
                
                for (const proprietario of dados.proprietarios) {
                    if (proprietario.uuid_local) {
                        await window.dbManager.updateProprietarioUuid(proprietario.id, proprietario.uuid_local);
                    }
                }
                
                for (const ocorrencia of dados.ocorrencias) {
                    if (ocorrencia.uuid_local) {
                        await window.dbManager.updateOcorrenciaUuid(ocorrencia.id, ocorrencia.uuid_local);
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao atualizar UUIDs locais:', error);
        }
    }
    
    /**
     * Obtém status de sincronização do servidor
     */
    async obterStatusSincronizacao() {
        const usuario = this.getUsuario();
        if (!usuario || !this.isOnline) {
            return null;
        }
        
        try {
            const response = await fetch(`${this.serverUrl}/sincronizar/status/${encodeURIComponent(usuario)}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Erro ao obter status:', error);
        }
        
        return null;
    }
    
    /**
     * Obtém histórico de sincronizações
     */
    async obterHistoricoSincronizacao(limit = 10) {
        const usuario = this.getUsuario();
        if (!usuario || !this.isOnline) {
            return [];
        }
        
        try {
            const response = await fetch(`${this.serverUrl}/sincronizar/historico/${encodeURIComponent(usuario)}?limit=${limit}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Erro ao obter histórico:', error);
        }
        
        return [];
    }
    
    /**
     * Mostra indicador de progresso
     */
    showSyncProgress(message) {
        let progressDiv = document.getElementById('sync-progress');
        if (!progressDiv) {
            progressDiv = document.createElement('div');
            progressDiv.id = 'sync-progress';
            progressDiv.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #007bff;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                z-index: 1000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            `;
            document.body.appendChild(progressDiv);
        }
        
        progressDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 20px; height: 20px; border: 2px solid #fff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <span>${message}</span>
            </div>
        `;
        
        // Adicionar CSS da animação se não existir
        if (!document.getElementById('sync-spinner-style')) {
            const style = document.createElement('style');
            style.id = 'sync-spinner-style';
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    /**
     * Esconde indicador de progresso
     */
    hideSyncProgress() {
        const progressDiv = document.getElementById('sync-progress');
        if (progressDiv) {
            progressDiv.remove();
        }
    }
    
    /**
     * Obtém informações da última sincronização local
     */
    getLastSyncInfo() {
        const lastSyncStr = localStorage.getItem('secrimpo_last_sync');
        if (lastSyncStr) {
            return new Date(lastSyncStr);
        }
        return null;
    }
    
    /**
     * Verifica se é necessário sincronizar (baseado em tempo)
     */
    needsSync(maxHours = 24) {
        const lastSync = this.getLastSyncInfo();
        if (!lastSync) return true;
        
        const now = new Date();
        const diffHours = (now - lastSync) / (1000 * 60 * 60);
        return diffHours >= maxHours;
    }
}

// Instância global
window.syncManager = new SyncManager();

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SyncManager;
}