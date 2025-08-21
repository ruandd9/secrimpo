const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: false // Para desenvolvimento
    },
    title: 'SECRIMPO - Sistema de Registro de Ocorrências',
    show: false // Não mostra até estar pronto
  });

  // Mostra quando estiver pronto
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.loadFile('src/index.html');

  // Abre DevTools em desenvolvimento
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Desabilita aceleração de hardware para evitar problemas de GPU no Windows
app.disableHardwareAcceleration();

// Adiciona argumentos para resolver problemas comuns
app.commandLine.appendSwitch('disable-gpu');
app.commandLine.appendSwitch('disable-gpu-sandbox');

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers para comunicação com o renderer
ipcMain.handle('api-request', async (event, { method, url, data }) => {
  const axios = require('axios');
  const baseURL = 'http://127.0.0.1:8000';
  
  try {
    const response = await axios({
      method,
      url: `${baseURL}${url}`,
      data,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data || error.message 
    };
  }
});