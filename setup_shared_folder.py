#!/usr/bin/env python3
"""
SECRIMPO - Configurador de Pasta Compartilhada
Script para configurar facilmente uma pasta compartilhada para múltiplos usuários
"""
import os
import sys
from pathlib import Path

def main():
    """Configurador principal"""
    print("=" * 70)
    print("🗂️  SECRIMPO - Configurador de Pasta Compartilhada")
    print("=" * 70)
    print()
    print("Este script irá configurar uma pasta compartilhada onde múltiplos")
    print("usuários podem inserir e acessar dados do SECRIMPO simultaneamente.")
    print()
    
    # Verificar se já existe configuração
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Erro: Execute este script na pasta raiz do projeto SECRIMPO")
        print("   (onde estão as pastas 'backend' e 'frontend')")
        return False
    
    config_file = backend_dir / "shared_config.json"
    if config_file.exists():
        print("⚠️  Já existe uma configuração de pasta compartilhada.")
        choice = input("Deseja reconfigurar? (s/N): ").strip().lower()
        if choice not in ['s', 'sim', 'y', 'yes']:
            print("Configuração mantida. Saindo...")
            return True
    
    print("\n📁 Opções de Pasta Compartilhada:")
    print()
    print("1. 💻 Pasta Local Compartilhada")
    print("   - Cria uma pasta no computador atual")
    print("   - Outros usuários acessam via rede")
    print("   - Exemplo: C:\\SecrimpoShared")
    print()
    print("2. 🌐 Pasta de Rede (SMB/CIFS)")
    print("   - Pasta em servidor de arquivos")
    print("   - Exemplo: \\\\servidor\\SecrimpoData")
    print()
    print("3. 💾 Unidade Mapeada")
    print("   - Unidade de rede já mapeada")
    print("   - Exemplo: Z:\\SecrimpoData")
    print()
    print("4. 🔍 Detectar Automaticamente")
    print("   - Procura pastas compartilhadas existentes")
    print()
    
    while True:
        choice = input("Escolha uma opção (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            break
        print("❌ Opção inválida. Digite 1, 2, 3 ou 4.")
    
    shared_path = None
    
    if choice == '1':
        # Pasta local compartilhada
        print("\n💻 Configurando Pasta Local Compartilhada...")
        default_path = "C:\\SecrimpoShared" if os.name == 'nt' else "/home/shared/secrimpo"
        path_input = input(f"Digite o caminho da pasta (Enter para '{default_path}'): ").strip()
        shared_path = path_input if path_input else default_path
        
        # Criar pasta se não existir
        try:
            Path(shared_path).mkdir(parents=True, exist_ok=True)
            print(f"✅ Pasta criada: {shared_path}")
            
            # Instruções para compartilhamento
            print(f"\n📋 Para compartilhar esta pasta com outros usuários:")
            if os.name == 'nt':  # Windows
                print(f"1. Clique com botão direito na pasta: {shared_path}")
                print(f"2. Selecione 'Propriedades' > 'Compartilhamento'")
                print(f"3. Clique em 'Compartilhamento Avançado'")
                print(f"4. Marque 'Compartilhar esta pasta'")
                print(f"5. Em 'Permissões', adicione 'Todos' com 'Controle Total'")
            else:  # Linux
                print(f"1. Instale o Samba: sudo apt install samba")
                print(f"2. Edite /etc/samba/smb.conf e adicione:")
                print(f"   [secrimpo]")
                print(f"   path = {shared_path}")
                print(f"   browseable = yes")
                print(f"   writable = yes")
                print(f"   guest ok = yes")
                print(f"3. Reinicie o Samba: sudo systemctl restart smbd")
        
        except Exception as e:
            print(f"❌ Erro ao criar pasta: {e}")
            return False
    
    elif choice == '2':
        # Pasta de rede
        print("\n🌐 Configurando Pasta de Rede...")
        print("Exemplos:")
        print("  Windows: \\\\servidor\\SecrimpoData")
        print("  Linux: //servidor/SecrimpoData")
        shared_path = input("Digite o caminho da rede: ").strip()
        
        if not shared_path:
            print("❌ Caminho não pode estar vazio")
            return False
    
    elif choice == '3':
        # Unidade mapeada
        print("\n💾 Configurando Unidade Mapeada...")
        print("Exemplos: Z:\\SecrimpoData, /mnt/secrimpo")
        shared_path = input("Digite o caminho da unidade mapeada: ").strip()
        
        if not shared_path:
            print("❌ Caminho não pode estar vazio")
            return False
    
    elif choice == '4':
        # Detectar automaticamente
        print("\n🔍 Detectando pastas compartilhadas...")
        possible_paths = [
            "C:\\SecrimpoShared",
            "\\\\servidor\\SecrimpoData",
            "Z:\\SecrimpoData",
            "/home/shared/secrimpo",
            "/mnt/secrimpo",
            "/media/secrimpo"
        ]
        
        found_paths = []
        for path in possible_paths:
            if os.path.exists(path):
                found_paths.append(path)
        
        if found_paths:
            print("✅ Pastas encontradas:")
            for i, path in enumerate(found_paths, 1):
                print(f"  {i}. {path}")
            
            while True:
                try:
                    idx = int(input(f"Escolha uma pasta (1-{len(found_paths)}): ")) - 1
                    if 0 <= idx < len(found_paths):
                        shared_path = found_paths[idx]
                        break
                    else:
                        print(f"❌ Digite um número entre 1 e {len(found_paths)}")
                except ValueError:
                    print("❌ Digite um número válido")
        else:
            print("❌ Nenhuma pasta compartilhada encontrada automaticamente")
            print("   Configure manualmente usando as opções 1, 2 ou 3")
            return False
    
    # Executar configuração
    print(f"\n⚙️  Configurando armazenamento compartilhado...")
    print(f"📁 Pasta: {shared_path}")
    
    try:
        # Importar e executar configuração
        sys.path.append(str(backend_dir))
        from shared_storage import SharedStorageManager
        
        # Inicializar gerenciador
        storage = SharedStorageManager(shared_path)
        
        # Testar conectividade
        is_connected, message = storage.test_connectivity()
        
        if not is_connected:
            print(f"❌ {message}")
            print("\n💡 Possíveis soluções:")
            print("- Verifique se a pasta existe e está acessível")
            print("- Confirme permissões de leitura/escrita")
            print("- Teste conectividade de rede (se aplicável)")
            return False
        
        print(f"✅ {message}")
        
        # Configurar banco compartilhado
        print(f"📊 Configurando banco de dados...")
        db_path = storage.setup_shared_database()
        print(f"✅ Banco configurado: {db_path}")
        
        # Criar backup inicial
        print(f"💾 Criando backup inicial...")
        backup_path = storage.create_backup()
        if backup_path:
            print(f"✅ Backup criado: {backup_path}")
        
        # Salvar configuração
        config_data = {
            "setup_method": choice,
            "user_input": shared_path,
            "setup_by": os.getenv("USERNAME", "unknown")
        }
        storage.save_config(config_data)
        
        print(f"\n🎉 Configuração concluída com sucesso!")
        print(f"\n📋 Resumo da Configuração:")
        print(f"   📁 Pasta Compartilhada: {storage.shared_path}")
        print(f"   📊 Banco de Dados: {storage.get_database_path()}")
        print(f"   📤 Exportações: {storage.get_exports_path()}")
        print(f"   💾 Backups: {storage.shared_path / 'backups'}")
        
        print(f"\n📝 Próximos Passos:")
        print(f"1. 👥 Compartilhe a pasta com outros usuários (se ainda não fez)")
        print(f"2. 💻 Execute este script em cada PC que usará o SECRIMPO")
        print(f"3. 🚀 Inicie o SECRIMPO normalmente: python backend/start_api.py")
        print(f"4. 🔄 Todos os usuários verão os mesmos dados automaticamente")
        
        print(f"\n⚠️  Importante:")
        print(f"- Faça backup regular da pasta: {storage.shared_path}")
        print(f"- Mantenha a pasta sempre acessível na rede")
        print(f"- Em caso de problemas, consulte os logs em: {storage.shared_path / 'logs'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante configuração: {e}")
        print(f"\n🔧 Para resolver:")
        print(f"1. Verifique se Python está instalado corretamente")
        print(f"2. Execute: pip install -r backend/requirements.txt")
        print(f"3. Tente novamente")
        return False


if __name__ == "__main__":
    try:
        success = main()
        if success:
            input("\n✅ Pressione Enter para sair...")
        else:
            input("\n❌ Pressione Enter para sair...")
    except KeyboardInterrupt:
        print("\n\n⏹️  Configuração cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("Pressione Enter para sair...")