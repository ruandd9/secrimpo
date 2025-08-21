const { contextBridge, ipcRenderer } = require('electron');

// Expõe APIs seguras para o renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // API para fazer requisições HTTP
  apiRequest: (method, url, data) => ipcRenderer.invoke('api-request', { method, url, data }),
  
  // Utilitários
  platform: process.platform,
  versions: process.versions
});

// API específica para SECRIMPO
contextBridge.exposeInMainWorld('secrimpoAPI', {
  // Policiais
  criarPolicial: (data) => ipcRenderer.invoke('api-request', { method: 'POST', url: '/policiais/', data }),
  listarPoliciais: () => ipcRenderer.invoke('api-request', { method: 'GET', url: '/policiais/' }),
  obterPolicial: (id) => ipcRenderer.invoke('api-request', { method: 'GET', url: `/policiais/${id}` }),
  
  // Proprietários
  criarProprietario: (data) => ipcRenderer.invoke('api-request', { method: 'POST', url: '/proprietarios/', data }),
  listarProprietarios: () => ipcRenderer.invoke('api-request', { method: 'GET', url: '/proprietarios/' }),
  
  // Ocorrências
  criarOcorrencia: (data) => ipcRenderer.invoke('api-request', { method: 'POST', url: '/ocorrencias/', data }),
  listarOcorrencias: () => ipcRenderer.invoke('api-request', { method: 'GET', url: '/ocorrencias/' }),
  
  // Itens
  criarItem: (data) => ipcRenderer.invoke('api-request', { method: 'POST', url: '/itens/', data }),
  listarItens: () => ipcRenderer.invoke('api-request', { method: 'GET', url: '/itens/' }),
  listarItensPorOcorrencia: (id) => ipcRenderer.invoke('api-request', { method: 'GET', url: `/itens/ocorrencia/${id}` }),
  
  // Estatísticas
  obterEstatisticas: () => ipcRenderer.invoke('api-request', { method: 'GET', url: '/estatisticas/' })
});