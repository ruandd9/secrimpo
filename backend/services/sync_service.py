"""
Serviço de sincronização entre clientes locais e servidor central
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Importar modelos existentes
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import Policial, Proprietario, Ocorrencia, ItemApreendido
from models.sync_models import SyncLog, RegistroSincronizado

class SyncService:
    """Serviço principal de sincronização"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def sincronizar_dados(self, usuario: str, client_uuid: str, dados: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Sincroniza dados do cliente com o servidor central
        
        Args:
            usuario: Nome/ID do usuário
            client_uuid: UUID único do cliente
            dados: Dicionário com os dados a sincronizar
            
        Returns:
            Resultado da sincronização
        """
        resultado = {
            "sucesso": True,
            "resumo": {},
            "detalhes": [],
            "erros": []
        }
        
        try:
            # Processar cada tipo de dado
            for tipo_dado, registros in dados.items():
                if tipo_dado == "policiais":
                    res = self._sincronizar_policiais(usuario, registros)
                elif tipo_dado == "proprietarios":
                    res = self._sincronizar_proprietarios(usuario, registros)
                elif tipo_dado == "ocorrencias":
                    res = self._sincronizar_ocorrencias(usuario, registros)
                else:
                    resultado["erros"].append(f"Tipo de dado desconhecido: {tipo_dado}")
                    continue
                
                resultado["resumo"][tipo_dado] = res
                resultado["detalhes"].extend(res.get("detalhes", []))
                if res.get("erros"):
                    resultado["erros"].extend(res["erros"])
            
            # Criar log de sincronização
            total_novos = sum(r.get("novos", 0) for r in resultado["resumo"].values())
            total_duplicados = sum(r.get("duplicados", 0) for r in resultado["resumo"].values())
            total_registros = total_novos + total_duplicados
            
            sync_log = SyncLog(
                usuario=usuario,
                client_uuid=client_uuid,
                total_registros=total_registros,
                registros_novos=total_novos,
                registros_duplicados=total_duplicados,
                status="sucesso" if not resultado["erros"] else "parcial",
                detalhes=json.dumps(resultado["resumo"])
            )
            
            self.db.add(sync_log)
            self.db.commit()
            
            resultado["sync_id"] = sync_log.id
            
        except Exception as e:
            self.db.rollback()
            resultado["sucesso"] = False
            resultado["erros"].append(f"Erro durante sincronização: {str(e)}")
        
        return resultado
    
    def _sincronizar_policiais(self, usuario: str, policiais: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sincroniza dados de policiais"""
        resultado = {"novos": 0, "duplicados": 0, "erros": [], "detalhes": []}
        
        for policial_data in policiais:
            try:
                uuid_local = policial_data.get("uuid_local")
                if not uuid_local:
                    resultado["erros"].append("Policial sem UUID local")
                    continue
                
                # Verificar se já foi sincronizado
                if self._ja_sincronizado(usuario, "policial", uuid_local):
                    resultado["duplicados"] += 1
                    continue
                
                # Verificar se já existe por matrícula
                matricula = policial_data.get("matricula")
                policial_existente = self.db.query(Policial).filter(
                    Policial.matricula == matricula
                ).first()
                
                if policial_existente:
                    # Marcar como sincronizado mesmo se já existia
                    self._marcar_sincronizado(usuario, "policial", uuid_local, policial_existente.id, policial_data)
                    resultado["duplicados"] += 1
                    resultado["detalhes"].append(f"Policial {matricula} já existia no sistema")
                else:
                    # Criar novo policial
                    novo_policial = Policial(
                        nome=policial_data["nome"],
                        matricula=policial_data["matricula"],
                        graduacao=policial_data["graduacao"],
                        unidade=policial_data["unidade"]
                    )
                    
                    self.db.add(novo_policial)
                    self.db.flush()  # Para obter o ID
                    
                    # Marcar como sincronizado
                    self._marcar_sincronizado(usuario, "policial", uuid_local, novo_policial.id, policial_data)
                    
                    resultado["novos"] += 1
                    resultado["detalhes"].append(f"Novo policial criado: {matricula}")
                
            except Exception as e:
                resultado["erros"].append(f"Erro ao sincronizar policial: {str(e)}")
        
        return resultado
    
    def _sincronizar_proprietarios(self, usuario: str, proprietarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sincroniza dados de proprietários"""
        resultado = {"novos": 0, "duplicados": 0, "erros": [], "detalhes": []}
        
        for prop_data in proprietarios:
            try:
                uuid_local = prop_data.get("uuid_local")
                if not uuid_local:
                    resultado["erros"].append("Proprietário sem UUID local")
                    continue
                
                # Verificar se já foi sincronizado
                if self._ja_sincronizado(usuario, "proprietario", uuid_local):
                    resultado["duplicados"] += 1
                    continue
                
                # Verificar se já existe por documento
                documento = prop_data.get("documento")
                prop_existente = self.db.query(Proprietario).filter(
                    Proprietario.documento == documento
                ).first()
                
                if prop_existente:
                    self._marcar_sincronizado(usuario, "proprietario", uuid_local, prop_existente.id, prop_data)
                    resultado["duplicados"] += 1
                    resultado["detalhes"].append(f"Proprietário {documento} já existia no sistema")
                else:
                    # Criar novo proprietário
                    novo_prop = Proprietario(
                        nome=prop_data["nome"],
                        documento=prop_data["documento"]
                    )
                    
                    self.db.add(novo_prop)
                    self.db.flush()
                    
                    self._marcar_sincronizado(usuario, "proprietario", uuid_local, novo_prop.id, prop_data)
                    
                    resultado["novos"] += 1
                    resultado["detalhes"].append(f"Novo proprietário criado: {documento}")
                
            except Exception as e:
                resultado["erros"].append(f"Erro ao sincronizar proprietário: {str(e)}")
        
        return resultado
    
    def _sincronizar_ocorrencias(self, usuario: str, ocorrencias: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sincroniza dados de ocorrências (mais complexo devido aos relacionamentos)"""
        resultado = {"novos": 0, "duplicados": 0, "erros": [], "detalhes": []}
        
        for ocor_data in ocorrencias:
            try:
                uuid_local = ocor_data.get("uuid_local")
                if not uuid_local:
                    resultado["erros"].append("Ocorrência sem UUID local")
                    continue
                
                # Verificar se já foi sincronizada
                if self._ja_sincronizado(usuario, "ocorrencia", uuid_local):
                    resultado["duplicados"] += 1
                    continue
                
                # Verificar se já existe por número genesis
                numero_genesis = ocor_data.get("numero_genesis")
                ocor_existente = self.db.query(Ocorrencia).filter(
                    Ocorrencia.numero_genesis == numero_genesis
                ).first()
                
                if ocor_existente:
                    self._marcar_sincronizado(usuario, "ocorrencia", uuid_local, ocor_existente.id, ocor_data)
                    resultado["duplicados"] += 1
                    resultado["detalhes"].append(f"Ocorrência {numero_genesis} já existia no sistema")
                else:
                    # Processar policial condutor
                    policial_data = ocor_data.get("policial_condutor", {})
                    policial_id = self._obter_ou_criar_policial(policial_data)
                    
                    if not policial_id:
                        resultado["erros"].append(f"Erro ao processar policial da ocorrência {numero_genesis}")
                        continue
                    
                    # Criar nova ocorrência
                    nova_ocorrencia = Ocorrencia(
                        numero_genesis=ocor_data["numero_genesis"],
                        unidade_fato=ocor_data["unidade_fato"],
                        data_apreensao=datetime.fromisoformat(ocor_data["data_apreensao"]).date(),
                        lei_infringida=ocor_data["lei_infringida"],
                        artigo=ocor_data["artigo"],
                        policial_condutor_id=policial_id
                    )
                    
                    self.db.add(nova_ocorrencia)
                    self.db.flush()
                    
                    # Processar itens apreendidos
                    itens_data = ocor_data.get("itens_apreendidos", [])
                    for item_data in itens_data:
                        # Processar proprietário do item
                        prop_data = item_data.get("proprietario", {})
                        prop_id = self._obter_ou_criar_proprietario(prop_data)
                        
                        if prop_id:
                            novo_item = ItemApreendido(
                                especie=item_data["especie"],
                                item=item_data["item"],
                                quantidade=item_data["quantidade"],
                                descricao_detalhada=item_data["descricao_detalhada"],
                                ocorrencia_id=nova_ocorrencia.id,
                                proprietario_id=prop_id,
                                policial_id=policial_id
                            )
                            self.db.add(novo_item)
                    
                    self._marcar_sincronizado(usuario, "ocorrencia", uuid_local, nova_ocorrencia.id, ocor_data)
                    
                    resultado["novos"] += 1
                    resultado["detalhes"].append(f"Nova ocorrência criada: {numero_genesis}")
                
            except Exception as e:
                resultado["erros"].append(f"Erro ao sincronizar ocorrência: {str(e)}")
        
        return resultado
    
    def _ja_sincronizado(self, usuario: str, tipo: str, uuid_local: str) -> bool:
        """Verifica se um registro já foi sincronizado"""
        return self.db.query(RegistroSincronizado).filter(
            and_(
                RegistroSincronizado.usuario == usuario,
                RegistroSincronizado.tipo_registro == tipo,
                RegistroSincronizado.uuid_local == uuid_local
            )
        ).first() is not None
    
    def _marcar_sincronizado(self, usuario: str, tipo: str, uuid_local: str, id_central: int, dados: Dict[str, Any]):
        """Marca um registro como sincronizado"""
        hash_dados = self._calcular_hash(dados)
        
        registro_sync = RegistroSincronizado(
            usuario=usuario,
            tipo_registro=tipo,
            uuid_local=uuid_local,
            id_central=id_central,
            hash_dados=hash_dados
        )
        
        self.db.add(registro_sync)
    
    def _calcular_hash(self, dados: Dict[str, Any]) -> str:
        """Calcula hash dos dados para detectar mudanças"""
        dados_str = json.dumps(dados, sort_keys=True, default=str)
        return hashlib.md5(dados_str.encode()).hexdigest()
    
    def _obter_ou_criar_policial(self, policial_data: Dict[str, Any]) -> Optional[int]:
        """Obtém ID de policial existente ou cria novo"""
        if not policial_data.get("matricula"):
            return None
        
        policial = self.db.query(Policial).filter(
            Policial.matricula == policial_data["matricula"]
        ).first()
        
        if not policial:
            policial = Policial(
                nome=policial_data["nome"],
                matricula=policial_data["matricula"],
                graduacao=policial_data["graduacao"],
                unidade=policial_data["unidade"]
            )
            self.db.add(policial)
            self.db.flush()
        
        return policial.id
    
    def _obter_ou_criar_proprietario(self, prop_data: Dict[str, Any]) -> Optional[int]:
        """Obtém ID de proprietário existente ou cria novo"""
        if not prop_data.get("documento"):
            return None
        
        proprietario = self.db.query(Proprietario).filter(
            Proprietario.documento == prop_data["documento"]
        ).first()
        
        if not proprietario:
            proprietario = Proprietario(
                nome=prop_data["nome"],
                documento=prop_data["documento"]
            )
            self.db.add(proprietario)
            self.db.flush()
        
        return proprietario.id
    
    def obter_status_sincronizacao(self, usuario: str) -> Dict[str, Any]:
        """Obtém status de sincronização de um usuário"""
        ultima_sync = self.db.query(SyncLog).filter(
            SyncLog.usuario == usuario
        ).order_by(SyncLog.timestamp.desc()).first()
        
        total_syncs = self.db.query(SyncLog).filter(
            SyncLog.usuario == usuario
        ).count()
        
        total_registros = self.db.query(RegistroSincronizado).filter(
            RegistroSincronizado.usuario == usuario
        ).count()
        
        return {
            "usuario": usuario,
            "ultima_sincronizacao": ultima_sync.timestamp if ultima_sync else None,
            "total_sincronizacoes": total_syncs,
            "total_registros_sincronizados": total_registros,
            "status_ultima_sync": ultima_sync.status if ultima_sync else "nunca_sincronizado"
        }