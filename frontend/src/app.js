// Estado da aplicação
let appState = {
    policiais: [],
    proprietarios: [],
    currentPolicial: null,
    currentProprietario: null,
    itemCount: 1
};

// Mapeamento de itens por espécie
const itemsPorEspecie = {
    'Entorpecente': ['Maconha', 'Cocaína', 'Crack', 'Ecstasy', 'LSD', 'Heroína', 'Outros'],
    'Arma': ['Pistola', 'Revólver', 'Rifle', 'Espingarda', 'Arma Branca', 'Outros'],
    'Munição': ['Cartuchos', 'Balas', 'Projéteis', 'Outros'],
    'Documento': ['RG', 'CPF', 'CNH', 'Passaporte', 'Certidão', 'Outros'],
    'Dinheiro': ['Real', 'Dólar', 'Euro', 'Outros'],
    'Eletrônico': ['Celular', 'Notebook', 'Tablet', 'TV', 'Som', 'Outros'],
    'Veículo': ['Carro', 'Moto', 'Bicicleta', 'Caminhão', 'Outros'],
    'Outros': ['Diversos']
};

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[ROCKET] Iniciando SECRIMPO Frontend...');

    // Carrega dados iniciais
    await loadInitialData();

    // Configura event listeners
    setupEventListeners();

    // Configura data atual
    document.getElementById('dataApreensao').valueAsDate = new Date();

    console.log('[CHECK] SECRIMPO Frontend carregado com sucesso!');
});

// Carrega dados iniciais da API
async function loadInitialData() {
    try {
        showLoading(true);

        // Carrega policiais
        const policiaisResponse = await window.secrimpoAPI.listarPoliciais();
        if (policiaisResponse.success) {
            appState.policiais = policiaisResponse.data;
            console.log(`[CLIPBOARD-LIST] ${appState.policiais.length} policiais carregados`);
        }

        // Carrega proprietários
        const proprietariosResponse = await window.secrimpoAPI.listarProprietarios();
        if (proprietariosResponse.success) {
            appState.proprietarios = proprietariosResponse.data;
            console.log(`[CLIPBOARD-LIST] ${appState.proprietarios.length} proprietários carregados`);
        }

    } catch (error) {
        console.error('[TIMES] Erro ao carregar dados iniciais:', error);
        showMessage('Erro ao conectar com a API. Verifique se o servidor está rodando.', 'error');
    } finally {
        showLoading(false);
    }
}

// Configura event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('secrimpoForm').addEventListener('submit', handleFormSubmit);

    // Espécie change para atualizar itens
    document.addEventListener('change', (e) => {
        if (e.target.name && e.target.name.startsWith('especie_')) {
            updateItemOptions(e.target);
        }
    });

    // Auto-complete para policial
    document.getElementById('policialMatricula').addEventListener('blur', buscarPolicialPorMatricula);

    // Auto-complete para proprietário
    document.getElementById('proprietarioDocumento').addEventListener('blur', buscarProprietarioPorDocumento);
    
    // Máscara de documento
    document.getElementById('proprietarioDocumento').addEventListener('input', applyDocumentMask);
    document.getElementById('proprietarioDocumento').addEventListener('blur', validateDocument);
    
    // Tipo de documento change
    document.getElementById('tipoDocumento').addEventListener('change', updateDocumentMask);
}

// Manipula o envio do formulário
async function handleFormSubmit(e) {
    e.preventDefault();

    if (!validateForm()) {
        showMessage('Por favor, preencha todos os campos obrigatórios.', 'error');
        return;
    }

    try {
        showLoading(true);

        // 1. Criar/obter policial
        const policial = await createOrGetPolicial();
        if (!policial) return;

        // 2. Criar/obter proprietário
        const proprietario = await createOrGetProprietario();
        if (!proprietario) return;

        // 3. Criar ocorrência
        const ocorrencia = await createOcorrencia(policial.id);
        if (!ocorrencia) return;

        // 4. Criar itens apreendidos
        await createItensApreendidos(ocorrencia.id, proprietario.id, policial.id);

        showMessage('Termo de apreensão salvo com sucesso!', 'success');

        // Reset form após sucesso
        setTimeout(() => {
            if (confirm('Deseja criar um novo termo de apreensão?')) {
                resetForm();
            }
        }, 2000);

    } catch (error) {
        console.error('[TIMES] Erro ao salvar:', error);
        showMessage('Erro ao salvar o termo de apreensão.', 'error');
    } finally {
        showLoading(false);
    }
}

// Cria ou obtém policial
async function createOrGetPolicial() {
    const nome = document.getElementById('policialNome').value.trim();
    const matricula = document.getElementById('policialMatricula').value.trim();
    const graduacao = document.getElementById('policialGraduacao').value.trim();
    const unidade = document.getElementById('policialUnidade').value.trim();

    // Verifica se já existe
    const existente = appState.policiais.find(p => p.matricula === matricula);
    if (existente) {
        return existente;
    }

    // Cria novo
    const response = await window.secrimpoAPI.criarPolicial({
        nome, matricula, graduacao, unidade
    });

    if (response.success) {
        appState.policiais.push(response.data);
        return response.data;
    } else {
        showMessage(`Erro ao criar policial: ${response.error.detail || response.error}`, 'error');
        return null;
    }
}

// Cria ou obtém proprietário
async function createOrGetProprietario() {
    const nome = document.getElementById('proprietarioNome').value.trim();
    const documento = document.getElementById('proprietarioDocumento').value.trim();

    // Verifica se já existe
    const existente = appState.proprietarios.find(p => p.documento === documento);
    if (existente) {
        return existente;
    }

    // Cria novo
    const response = await window.secrimpoAPI.criarProprietario({
        nome, documento
    });

    if (response.success) {
        appState.proprietarios.push(response.data);
        return response.data;
    } else {
        showMessage(`Erro ao criar proprietário: ${response.error.detail || response.error}`, 'error');
        return null;
    }
}

// Cria ocorrência
async function createOcorrencia(policialId) {
    const ocorrenciaData = {
        numero_genesis: document.getElementById('numeroGenesis').value.trim(),
        unidade_fato: document.getElementById('unidadeFato').value.trim(),
        data_apreensao: document.getElementById('dataApreensao').value,
        lei_infringida: document.getElementById('leiInfringida').value.trim(),
        artigo: document.getElementById('artigo').value.trim(),
        policial_condutor_id: policialId
    };

    const response = await window.secrimpoAPI.criarOcorrencia(ocorrenciaData);

    if (response.success) {
        return response.data;
    } else {
        showMessage(`Erro ao criar ocorrência: ${response.error.detail || response.error}`, 'error');
        return null;
    }
}

// Cria itens apreendidos
async function createItensApreendidos(ocorrenciaId, proprietarioId, policialId) {
    const itemRows = document.querySelectorAll('.item-row');

    for (let i = 0; i < itemRows.length; i++) {
        const row = itemRows[i];
        const index = row.dataset.itemIndex;

        const itemData = {
            especie: document.getElementById(`especie_${index}`).value,
            item: document.getElementById(`item_${index}`).value,
            quantidade: parseInt(document.getElementById(`quantidade_${index}`).value),
            descricao_detalhada: document.getElementById(`descricao_${index}`).value.trim(),
            ocorrencia_id: ocorrenciaId,
            proprietario_id: proprietarioId,
            policial_id: policialId
        };

        const response = await window.secrimpoAPI.criarItem(itemData);

        if (!response.success) {
            showMessage(`Erro ao criar item ${i + 1}: ${response.error.detail || response.error}`, 'error');
            throw new Error(`Erro ao criar item ${i + 1}`);
        }
    }
}

// Adiciona novo item
function addItem() {
    const container = document.getElementById('itemsContainer');
    const newIndex = appState.itemCount++;

    const itemRow = document.createElement('div');
    itemRow.className = 'item-row';
    itemRow.dataset.itemIndex = newIndex;

    itemRow.innerHTML = `
        <div class="form-row">
            <div class="form-group">
                <label for="especie_${newIndex}">Espécie</label>
                <select id="especie_${newIndex}" name="especie_${newIndex}" required>
                    <option value="">Selecione a Espécie</option>
                    <option value="Entorpecente">Entorpecente</option>
                    <option value="Arma">Arma</option>
                    <option value="Munição">Munição</option>
                    <option value="Documento">Documento</option>
                    <option value="Dinheiro">Dinheiro</option>
                    <option value="Eletrônico">Eletrônico</option>
                    <option value="Veículo">Veículo</option>
                    <option value="Outros">Outros</option>
                </select>
            </div>
            <div class="form-group">
                <label for="item_${newIndex}">Item</label>
                <select id="item_${newIndex}" name="item_${newIndex}" required>
                    <option value="">Selecione o Item</option>
                </select>
            </div>
            <div class="form-group">
                <label for="quantidade_${newIndex}">Quantidade</label>
                <input type="number" id="quantidade_${newIndex}" name="quantidade_${newIndex}" min="1" required>
            </div>
            <div class="form-group full-width">
                <label for="descricao_${newIndex}">Descrição</label>
                <textarea id="descricao_${newIndex}" name="descricao_${newIndex}" placeholder="Descrição Detalhada" rows="3" required></textarea>
            </div>
        </div>
        <button type="button" class="btn-remove-item" onclick="removeItem(${newIndex})"><i class="fas fa-times"></i></button>
    `;

    container.appendChild(itemRow);

    // Mostra botão de remover se há mais de um item
    updateRemoveButtons();
}

// Remove item
function removeItem(index) {
    const itemRow = document.querySelector(`[data-item-index="${index}"]`);
    if (itemRow) {
        itemRow.remove();
        updateRemoveButtons();
    }
}

// Atualiza visibilidade dos botões de remover
function updateRemoveButtons() {
    const itemRows = document.querySelectorAll('.item-row');
    const removeButtons = document.querySelectorAll('.btn-remove-item');

    removeButtons.forEach(btn => {
        btn.style.display = itemRows.length > 1 ? 'flex' : 'none';
    });
}

// Atualiza opções de item baseado na espécie
function updateItemOptions(especieSelect) {
    const index = especieSelect.name.split('_')[1];
    const itemSelect = document.getElementById(`item_${index}`);
    const especie = especieSelect.value;

    // Limpa opções atuais
    itemSelect.innerHTML = '<option value="">Selecione o Item</option>';

    // Adiciona novas opções
    if (especie && itemsPorEspecie[especie]) {
        itemsPorEspecie[especie].forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            itemSelect.appendChild(option);
        });
    }
}

// Busca policial por matrícula
async function buscarPolicialPorMatricula() {
    const matricula = document.getElementById('policialMatricula').value.trim();
    if (!matricula) return;

    const policial = appState.policiais.find(p => p.matricula === matricula);
    if (policial) {
        document.getElementById('policialNome').value = policial.nome;
        document.getElementById('policialGraduacao').value = policial.graduacao;
        document.getElementById('policialUnidade').value = policial.unidade;
        appState.currentPolicial = policial;
    }
}

// Busca proprietário por documento
async function buscarProprietarioPorDocumento() {
    const documento = document.getElementById('proprietarioDocumento').value.trim();
    if (!documento) return;

    const proprietario = appState.proprietarios.find(p => p.documento === documento);
    if (proprietario) {
        document.getElementById('proprietarioNome').value = proprietario.nome;
        appState.currentProprietario = proprietario;
    }
}

// Buscar policial (botão)
function buscarPolicial() {
    // Implementar modal de busca se necessário
    showMessage('Digite a matrícula e pressione Tab para busca automática', 'warning');
}

// Novo policial (botão)
function novoPolicial() {
    document.getElementById('policialNome').value = '';
    document.getElementById('policialMatricula').value = '';
    document.getElementById('policialGraduacao').value = '';
    document.getElementById('policialUnidade').value = '';
    appState.currentPolicial = null;
}

// Buscar proprietário (botão)
function buscarProprietario() {
    // Implementar modal de busca se necessário
    showMessage('Digite o documento e pressione Tab para busca automática', 'warning');
}

// Novo proprietário (botão)
function novoProprietario() {
    document.getElementById('proprietarioNome').value = '';
    document.getElementById('proprietarioDocumento').value = '';
    appState.currentProprietario = null;
}

// Validação do formulário
function validateForm() {
    const requiredFields = [
        'numeroGenesis', 'unidadeFato', 'dataApreensao', 'leiInfringida', 'artigo',
        'proprietarioNome', 'proprietarioDocumento',
        'policialNome', 'policialMatricula', 'policialGraduacao', 'policialUnidade'
    ];

    let isValid = true;

    // Valida campos básicos
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (!field.value.trim()) {
            field.classList.add('invalid');
            isValid = false;
        } else {
            field.classList.remove('invalid');
        }
    });

    // Valida itens
    const itemRows = document.querySelectorAll('.item-row');
    itemRows.forEach(row => {
        const index = row.dataset.itemIndex;
        const fields = [`especie_${index}`, `item_${index}`, `quantidade_${index}`, `descricao_${index}`];

        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (!field.value.trim()) {
                field.classList.add('invalid');
                isValid = false;
            } else {
                field.classList.remove('invalid');
            }
        });
    });

    return isValid;
}

// Reset do formulário
function resetForm() {
    document.getElementById('secrimpoForm').reset();
    document.getElementById('dataApreensao').valueAsDate = new Date();

    // Remove itens extras
    const container = document.getElementById('itemsContainer');
    const itemRows = container.querySelectorAll('.item-row');
    for (let i = 1; i < itemRows.length; i++) {
        itemRows[i].remove();
    }

    // Reset primeiro item
    const firstRow = container.querySelector('.item-row');
    firstRow.dataset.itemIndex = '0';
    firstRow.querySelector('select[name="especie_0"]').selectedIndex = 0;
    firstRow.querySelector('select[name="item_0"]').innerHTML = '<option value="">Selecione o Item</option>';

    // Reset documento
    updateDocumentMask();
    
    // Remove classes de validação
    document.querySelectorAll('.valid, .invalid').forEach(el => {
        el.classList.remove('valid', 'invalid');
    });

    appState.itemCount = 1;
    appState.currentPolicial = null;
    appState.currentProprietario = null;

    updateRemoveButtons();
}

// Utilitários de UI
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

function showMessage(message, type = 'info') {
    const container = document.getElementById('messageContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;

    container.appendChild(messageDiv);

    // Remove após 5 segundos
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// === FUNÇÕES DE MÁSCARA E VALIDAÇÃO ===

// Atualiza máscara do documento baseado no tipo selecionado
function updateDocumentMask() {
    const tipoDocumento = document.getElementById('tipoDocumento').value;
    const documentoInput = document.getElementById('proprietarioDocumento');
    const hint = document.getElementById('documentoHint');
    
    // Limpa o campo
    documentoInput.value = '';
    documentoInput.classList.remove('valid', 'invalid');
    
    if (tipoDocumento === 'CPF') {
        documentoInput.placeholder = '000.000.000-00';
        documentoInput.maxLength = 14;
        hint.textContent = 'Digite apenas números, a formatação será aplicada automaticamente';
        hint.className = 'input-hint';
    } else if (tipoDocumento === 'RG') {
        documentoInput.placeholder = '00.000.000-0';
        documentoInput.maxLength = 12;
        hint.textContent = 'Digite apenas números, a formatação será aplicada automaticamente';
        hint.className = 'input-hint';
    } else {
        documentoInput.placeholder = 'Selecione o tipo de documento primeiro';
        documentoInput.maxLength = 20;
        hint.textContent = '';
    }
}

// Aplica máscara durante a digitação
function applyDocumentMask(e) {
    const tipoDocumento = document.getElementById('tipoDocumento').value;
    let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito
    
    if (tipoDocumento === 'CPF') {
        // Máscara CPF: 000.000.000-00
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    } else if (tipoDocumento === 'RG') {
        // Máscara RG: 00.000.000-0
        value = value.replace(/(\d{2})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d{1})$/, '$1-$2');
    }
    
    e.target.value = value;
}

// Valida documento
function validateDocument() {
    const tipoDocumento = document.getElementById('tipoDocumento').value;
    const documentoInput = document.getElementById('proprietarioDocumento');
    const hint = document.getElementById('documentoHint');
    const value = documentoInput.value;
    
    if (!tipoDocumento) {
        hint.textContent = 'Selecione o tipo de documento primeiro';
        hint.className = 'input-hint invalid';
        documentoInput.classList.remove('valid');
        documentoInput.classList.add('invalid');
        return false;
    }
    
    let isValid = false;
    
    if (tipoDocumento === 'CPF') {
        isValid = validateCPF(value);
        hint.textContent = isValid ? 'CPF válido' : 'CPF inválido';
    } else if (tipoDocumento === 'RG') {
        isValid = validateRG(value);
        hint.textContent = isValid ? 'RG válido' : 'RG deve ter pelo menos 7 dígitos';
    }
    
    hint.className = `input-hint ${isValid ? 'valid' : 'invalid'}`;
    documentoInput.classList.toggle('valid', isValid);
    documentoInput.classList.toggle('invalid', !isValid);
    
    return isValid;
}

// Valida CPF
function validateCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    
    if (cpf.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(cpf)) return false; // Todos os dígitos iguais
    
    // Validação do primeiro dígito verificador
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let remainder = 11 - (sum % 11);
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(9))) return false;
    
    // Validação do segundo dígito verificador
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    remainder = 11 - (sum % 11);
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(10))) return false;
    
    return true;
}

// Valida RG (validação simples - apenas comprimento)
function validateRG(rg) {
    rg = rg.replace(/\D/g, '');
    return rg.length >= 7 && rg.length <= 9;
}

// Remove função novoPolicial (não é mais necessária)
// function novoPolicial() { ... } - REMOVIDA

// Atualiza busca de proprietário para considerar tipo de documento
async function buscarProprietarioPorDocumento() {
    const documento = document.getElementById('proprietarioDocumento').value.trim();
    const tipoDocumento = document.getElementById('tipoDocumento').value;
    
    if (!documento || !tipoDocumento) return;
    
    // Valida documento antes de buscar
    if (!validateDocument()) {
        showMessage('Documento inválido. Corrija antes de buscar.', 'error');
        return;
    }
    
    const proprietario = appState.proprietarios.find(p => p.documento === documento);
    if (proprietario) {
        document.getElementById('proprietarioNome').value = proprietario.nome;
        appState.currentProprietario = proprietario;
        showMessage('Proprietário encontrado!', 'success');
    } else {
        showMessage('Proprietário não encontrado. Será criado um novo registro.', 'warning');
    }
}

// Atualiza validação do formulário para incluir tipo de documento
function validateForm() {
    const requiredFields = [
        'numeroGenesis', 'unidadeFato', 'dataApreensao', 'leiInfringida', 'artigo',
        'proprietarioNome', 'tipoDocumento', 'proprietarioDocumento',
        'policialNome', 'policialMatricula', 'policialGraduacao', 'policialUnidade'
    ];
    
    let isValid = true;
    
    // Valida campos básicos
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (!field.value.trim()) {
            field.classList.add('invalid');
            isValid = false;
        } else {
            field.classList.remove('invalid');
        }
    });
    
    // Validação especial para documento
    if (!validateDocument()) {
        isValid = false;
    }
    
    // Valida itens
    const itemRows = document.querySelectorAll('.item-row');
    itemRows.forEach(row => {
        const index = row.dataset.itemIndex;
        const fields = [`especie_${index}`, `item_${index}`, `quantidade_${index}`, `descricao_${index}`];
        
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (!field.value.trim()) {
                field.classList.add('invalid');
                isValid = false;
            } else {
                field.classList.remove('invalid');
            }
        });
    });
    
    return isValid;
}

// Inicializa primeira espécie/item
document.addEventListener('DOMContentLoaded', () => {
    updateRemoveButtons();
    
    // Inicializa máscara de documento
    updateDocumentMask();
});