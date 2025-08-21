#!/usr/bin/env node
/**
 * Script para testar o frontend Electron
 */

const { spawn } = require('child_process');
const path = require('path');

console.log('🧪 Testando SECRIMPO Frontend...\n');

// Verifica se a API está rodando
async function checkAPI() {
    try {
        const response = await fetch('http://127.0.0.1:8000/');
        const data = await response.json();
        console.log('✅ API está rodando:', data.message);
        return true;
    } catch (error) {
        console.log('❌ API não está rodando. Inicie a API primeiro:');
        console.log('   cd backend && python start_api.py\n');
        return false;
    }
}

// Inicia o Electron
function startElectron() {
    console.log('🚀 Iniciando Electron...\n');

    const electronProcess = spawn('npm', ['start'], {
        cwd: __dirname,
        stdio: 'inherit',
        shell: true
    });

    electronProcess.on('error', (error) => {
        console.error('❌ Erro ao iniciar Electron:', error);
    });

    electronProcess.on('close', (code) => {
        console.log(`\n📱 Electron encerrado com código: ${code}`);
    });
}

// Função principal
async function main() {
    const apiRunning = await checkAPI();

    if (apiRunning) {
        startElectron();
    } else {
        console.log('⚠️  Inicie a API primeiro e tente novamente.');
        process.exit(1);
    }
}

// Executa se for chamado diretamente
if (require.main === module) {
    main().catch(console.error);
}