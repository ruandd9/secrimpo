# SECRIMPO Frontend - Electron

Interface gráfica do sistema SECRIMPO desenvolvida em Electron, replicando fielmente a interface original do sistema.

## 🚀 Funcionalidades

- ✅ **Formulário completo** de termo de apreensão
- ✅ **Integração com API** FastAPI
- ✅ **Validação em tempo real** dos campos
- ✅ **Auto-complete** para policiais e proprietários
- ✅ **Gestão dinâmica** de itens apreendidos
- ✅ **Interface responsiva** e moderna
- ✅ **Feedback visual** para usuário

## 📋 Pré-requisitos

- Node.js 16+ instalado
- API SECRIMPO rodando em `http://127.0.0.1:8000`

## 🛠️ Instalação

```bash
# Instalar dependências
npm install

# Iniciar aplicação
npm start

# Modo desenvolvimento (com DevTools)
npm run dev
```

## 🧪 Teste Completo

```bash
# 1. Inicie a API (em outro terminal)
cd ../backend
python start_api.py

# 2. Teste o frontend
node test-frontend.js
```

## 📁 Estrutura

```
frontend/
├── src/
│   ├── index.html      # Interface principal
│   ├── styles.css      # Estilos CSS
│   └── app.js          # Lógica JavaScript
├── assets/             # Imagens e recursos
├── main.js             # Processo principal Electron
├── preload.js          # Script de preload
└── package.json        # Configurações npm
```

## 🎯 Campos do Formulário

### Dados da Ocorrência
- Número Gênesis
- Unidade do Fato  
- Data da Apreensão
- Lei Infringida
- Artigo

### Itens Apreendidos
- Espécie (dropdown)
- Item (dropdown dependente)
- Quantidade
- Descrição detalhada
- ➕ Adicionar/remover itens dinamicamente

### Dados do Proprietário
- Nome
- RG/CPF
- 🔍 Busca automática por documento

### Dados do Policial
- Nome
- Matrícula
- Graduação
- Unidade
- 🔍 Busca automática por matrícula

## 🔄 Integração com API

O frontend se conecta automaticamente com a API SECRIMPO:

- **Policiais**: CRUD completo com busca por matrícula
- **Proprietários**: CRUD completo com busca por documento
- **Ocorrências**: Criação com validação de referências
- **Itens**: Múltiplos itens por ocorrência

## 🎨 Interface

A interface replica fielmente o design original:

- **Header** com logos institucionais
- **Seções organizadas** por tipo de dados
- **Cores institucionais** (azul PMDF)
- **Feedback visual** para ações do usuário
- **Responsividade** para diferentes tamanhos de tela

## 🔧 Desenvolvimento

Para modificar a interface:

1. **HTML**: Edite `src/index.html`
2. **CSS**: Edite `src/styles.css`  
3. **JavaScript**: Edite `src/app.js`
4. **Electron**: Edite `main.js` ou `preload.js`

## 📱 Build para Produção

```bash
# Instalar electron-builder
npm install -g electron-builder

# Build para Windows
npm run build
```

## 🐛 Troubleshooting

### API não conecta
- Verifique se a API está rodando em `http://127.0.0.1:8000`
- Teste: `curl http://127.0.0.1:8000/`

### Electron não inicia
- Verifique se o Node.js está instalado
- Execute: `npm install` novamente

### Campos não salvam
- Abra DevTools (F12) e verifique console
- Verifique se todos os campos obrigatórios estão preenchidos

## 📞 Suporte

Para problemas ou sugestões, verifique:
1. Console do navegador (F12)
2. Logs da API
3. Arquivo de configuração