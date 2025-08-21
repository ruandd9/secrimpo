import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.ocorrencia import Ocorrencia
from models.policial import Policial
from models.proprietario import Proprietario
from models.item_apreendido import ItemApreendido
from backend.services.crud_service import get_ocorrencias_por_periodo

class ExcelExportService:
    def __init__(self, db: Session):
        self.db = db
        self.export_dir = "exports"
        
        # Cria diretório de exports se não existir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def export_ocorrencias_completo(self, data_inicio: date, data_fim: date) -> str:
        """
        Exporta relatório completo de ocorrências com todos os dados relacionados
        """
        # Busca ocorrências no período
        ocorrencias = get_ocorrencias_por_periodo(self.db, data_inicio, data_fim)
        
        if not ocorrencias:
            raise ValueError("Nenhuma ocorrência encontrada no período especificado")
        
        # Prepara dados para o DataFrame
        dados_completos = []
        
        for ocorrencia in ocorrencias:
            # Dados básicos da ocorrência
            dados_base = {
                'ID_Ocorrencia': ocorrencia.id,
                'Numero_Genesis': ocorrencia.numero_genesis,
                'Unidade_Fato': ocorrencia.unidade_fato,
                'Data_Apreensao': ocorrencia.data_apreensao.strftime('%d/%m/%Y'),
                'Lei_Infringida': ocorrencia.lei_infringida,
                'Artigo': ocorrencia.artigo,
                'Policial_Condutor': ocorrencia.policial_condutor.nome,
                'Matricula_Condutor': ocorrencia.policial_condutor.matricula,
                'Graduacao_Condutor': ocorrencia.policial_condutor.graduacao,
                'Unidade_Condutor': ocorrencia.policial_condutor.unidade
            }
            
            # Se não há itens, adiciona linha só com dados da ocorrência
            if not ocorrencia.itens_apreendidos:
                dados_completos.append({
                    **dados_base,
                    'Item_Especie': '',
                    'Item_Nome': '',
                    'Item_Quantidade': '',
                    'Item_Descricao': '',
                    'Proprietario_Nome': '',
                    'Proprietario_Documento': '',
                    'Policial_Apreensor': '',
                    'Matricula_Apreensor': ''
                })
            else:
                # Adiciona uma linha para cada item apreendido
                for item in ocorrencia.itens_apreendidos:
                    dados_completos.append({
                        **dados_base,
                        'Item_Especie': item.especie,
                        'Item_Nome': item.item,
                        'Item_Quantidade': item.quantidade,
                        'Item_Descricao': item.descricao_detalhada,
                        'Proprietario_Nome': item.proprietario.nome,
                        'Proprietario_Documento': item.proprietario.documento,
                        'Policial_Apreensor': item.policial.nome,
                        'Matricula_Apreensor': item.policial.matricula
                    })
        
        # Cria DataFrame
        df = pd.DataFrame(dados_completos)
        
        # Nome do arquivo
        nome_arquivo = f"relatorio_completo_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.xlsx"
        caminho_arquivo = os.path.join(self.export_dir, nome_arquivo)
        
        # Exporta para Excel com formatação
        with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Relatório Completo', index=False)
            
            # Ajusta largura das colunas
            worksheet = writer.sheets['Relatório Completo']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return caminho_arquivo
    
    def export_resumo_mensal(self, ano: int, mes: int) -> str:
        """
        Exporta resumo mensal das ocorrências
        """
        # Define período do mês
        data_inicio = date(ano, mes, 1)
        if mes == 12:
            data_fim = date(ano + 1, 1, 1)
        else:
            data_fim = date(ano, mes + 1, 1)
        
        # Busca ocorrências
        ocorrencias = get_ocorrencias_por_periodo(self.db, data_inicio, data_fim)
        
        if not ocorrencias:
            raise ValueError(f"Nenhuma ocorrência encontrada em {mes:02d}/{ano}")
        
        # Prepara dados resumidos
        dados_resumo = []
        total_itens = 0
        
        for ocorrencia in ocorrencias:
            qtd_itens = len(ocorrencia.itens_apreendidos)
            total_itens += qtd_itens
            
            dados_resumo.append({
                'Data': ocorrencia.data_apreensao.strftime('%d/%m/%Y'),
                'Genesis': ocorrencia.numero_genesis,
                'Unidade': ocorrencia.unidade_fato,
                'Lei': ocorrencia.lei_infringida,
                'Artigo': ocorrencia.artigo,
                'Condutor': ocorrencia.policial_condutor.nome,
                'Qtd_Itens': qtd_itens
            })
        
        # Cria DataFrame
        df = pd.DataFrame(dados_resumo)
        
        # Adiciona linha de totais
        df_totais = pd.DataFrame([{
            'Data': 'TOTAL',
            'Genesis': '',
            'Unidade': '',
            'Lei': '',
            'Artigo': '',
            'Condutor': f'{len(ocorrencias)} ocorrências',
            'Qtd_Itens': total_itens
        }])
        
        df = pd.concat([df, df_totais], ignore_index=True)
        
        # Nome do arquivo
        nome_arquivo = f"resumo_mensal_{ano}_{mes:02d}.xlsx"
        caminho_arquivo = os.path.join(self.export_dir, nome_arquivo)
        
        # Exporta para Excel
        with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=f'Resumo {mes:02d}/{ano}', index=False)
            
            # Formatação
            worksheet = writer.sheets[f'Resumo {mes:02d}/{ano}']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return caminho_arquivo
    
    def export_por_policial(self, policial_id: int, data_inicio: date, data_fim: date) -> str:
        """
        Exporta relatório de ocorrências por policial específico
        """
        # Busca policial
        policial = self.db.query(Policial).filter(Policial.id == policial_id).first()
        if not policial:
            raise ValueError("Policial não encontrado")
        
        # Busca ocorrências do policial no período
        ocorrencias = self.db.query(Ocorrencia).filter(
            Ocorrencia.policial_condutor_id == policial_id,
            Ocorrencia.data_apreensao >= data_inicio,
            Ocorrencia.data_apreensao <= data_fim
        ).all()
        
        if not ocorrencias:
            raise ValueError(f"Nenhuma ocorrência encontrada para {policial.nome} no período")
        
        # Prepara dados
        dados_policial = []
        
        for ocorrencia in ocorrencias:
            for item in ocorrencia.itens_apreendidos:
                dados_policial.append({
                    'Data': ocorrencia.data_apreensao.strftime('%d/%m/%Y'),
                    'Genesis': ocorrencia.numero_genesis,
                    'Unidade': ocorrencia.unidade_fato,
                    'Lei': ocorrencia.lei_infringida,
                    'Artigo': ocorrencia.artigo,
                    'Item': item.item,
                    'Especie': item.especie,
                    'Quantidade': item.quantidade,
                    'Proprietario': item.proprietario.nome,
                    'Documento': item.proprietario.documento
                })
        
        # Cria DataFrame
        df = pd.DataFrame(dados_policial)
        
        # Nome do arquivo
        nome_arquivo = f"relatorio_{policial.nome.replace(' ', '_')}_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.xlsx"
        caminho_arquivo = os.path.join(self.export_dir, nome_arquivo)
        
        # Exporta para Excel
        with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=f'{policial.nome[:30]}', index=False)
            
            # Formatação
            worksheet = writer.sheets[f'{policial.nome[:30]}']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 40)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return caminho_arquivo
    
    def export_estatisticas(self, data_inicio: date, data_fim: date) -> str:
        """
        Exporta planilha com estatísticas do período
        """
        # Busca dados
        ocorrencias = get_ocorrencias_por_periodo(self.db, data_inicio, data_fim)
        
        if not ocorrencias:
            raise ValueError("Nenhuma ocorrência encontrada no período")
        
        # Estatísticas por lei
        stats_lei = {}
        stats_policial = {}
        stats_unidade = {}
        total_itens = 0
        
        for ocorrencia in ocorrencias:
            # Por lei
            lei = ocorrencia.lei_infringida
            if lei not in stats_lei:
                stats_lei[lei] = 0
            stats_lei[lei] += 1
            
            # Por policial
            policial = ocorrencia.policial_condutor.nome
            if policial not in stats_policial:
                stats_policial[policial] = 0
            stats_policial[policial] += 1
            
            # Por unidade
            unidade = ocorrencia.unidade_fato
            if unidade not in stats_unidade:
                stats_unidade[unidade] = 0
            stats_unidade[unidade] += 1
            
            # Total de itens
            total_itens += len(ocorrencia.itens_apreendidos)
        
        # Nome do arquivo
        nome_arquivo = f"estatisticas_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.xlsx"
        caminho_arquivo = os.path.join(self.export_dir, nome_arquivo)
        
        # Cria planilha com múltiplas abas
        with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
            # Aba resumo geral
            resumo_geral = pd.DataFrame([
                ['Total de Ocorrências', len(ocorrencias)],
                ['Total de Itens Apreendidos', total_itens],
                ['Período', f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"],
                ['Data do Relatório', datetime.now().strftime('%d/%m/%Y %H:%M')]
            ], columns=['Descrição', 'Valor'])
            resumo_geral.to_excel(writer, sheet_name='Resumo Geral', index=False)
            
            # Aba por lei
            df_lei = pd.DataFrame(list(stats_lei.items()), columns=['Lei', 'Quantidade'])
            df_lei = df_lei.sort_values('Quantidade', ascending=False)
            df_lei.to_excel(writer, sheet_name='Por Lei', index=False)
            
            # Aba por policial
            df_policial = pd.DataFrame(list(stats_policial.items()), columns=['Policial', 'Quantidade'])
            df_policial = df_policial.sort_values('Quantidade', ascending=False)
            df_policial.to_excel(writer, sheet_name='Por Policial', index=False)
            
            # Aba por unidade
            df_unidade = pd.DataFrame(list(stats_unidade.items()), columns=['Unidade', 'Quantidade'])
            df_unidade = df_unidade.sort_values('Quantidade', ascending=False)
            df_unidade.to_excel(writer, sheet_name='Por Unidade', index=False)
        
        return caminho_arquivo