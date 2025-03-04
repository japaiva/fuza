import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, HRFlowable, Indenter
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
import locale
import re
from functions.database import get_all_custos

# Configurar a localização para formatar números
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def format_currency(value):
    return locale.currency(value, grouping=True, symbol=None)

def gerar_pdf_demonstrativo(dimensionamento, explicacao, componentes, custo_total, respostas, respostas_agrupadas, grupos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=72, 
        leftMargin=72, 
        topMargin=72, 
        bottomMargin=18
    )
    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles['BodyText']
    subtitle_style = styles['Heading2']

    # ---- CRIANDO ESTILOS ESPECÍFICOS PARA O RELATÓRIO ----
    # Estilo para o título principal (mais profissional)
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1,  # centraliza o texto
        textColor=colors.black
    )
    
    # Estilo para texto em negrito
    bold_style = ParagraphStyle(
        'Bold', 
        parent=normal_style, 
        fontName='Helvetica-Bold'
    )

    # ---- CABEÇALHO (TÍTULO + LINHA) ----
    title_paragraph = Paragraph("Relatório de Cálculo do Elevador Fuza", title_style)
    elements.append(title_paragraph)
    
    # Linha horizontal logo abaixo do título
    hr = HRFlowable(
        width="100%",
        thickness=1,
        color=colors.black,
        spaceBefore=0.2 * inch,
        spaceAfter=0.3 * inch
    )
    elements.append(hr)

    # Informações do usuário, data e hora
    now = datetime.now()
    user_info = f"Usuário: {st.session_state.username} | Data: {now.strftime('%d/%m/%Y')} | Hora: {now.strftime('%H:%M:%S')}"
    elements.append(Paragraph(user_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # ---- 1. CONFIGURAÇÕES ----
    elements.append(Paragraph("1. Configurações", subtitle_style))
    
    for categoria, dados in respostas_agrupadas.items():
        elements.append(Paragraph(f"{categoria}:", bold_style))
        for chave, valor in dados.items():
            elements.append(Paragraph(f"{chave}: {valor}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    elements.append(Spacer(1, 0.2 * inch))

    # ---- 2. FICHA TÉCNICA ----
    elements.append(Paragraph("2. Ficha Técnica", subtitle_style))
    
    # Dimensões Cabine
    dim_cabine = f"""
    Dimensões Cabine: {dimensionamento['cab']['largura']:.2f}m L x {dimensionamento['cab']['compr']:.2f}m C x {dimensionamento['cab']['altura']:.2f}m A
    """
    elements.append(Paragraph(dim_cabine, normal_style))
    
    # Capacidade e Tração Cabine
    cap_tracao = f"""
    Capacidade e Tração Cabine: {format_currency(dimensionamento['cab']['capacidade'])} kg, {format_currency(dimensionamento['cab']['tracao'])} kg
    """
    elements.append(Paragraph(cap_tracao, normal_style))
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- 3. CÁLCULO DIMENSIONAMENTO ----
    elements.append(Paragraph("3. Cálculo Dimensionamento", subtitle_style))
    
    # Usar expressão regular para converter **texto** em <b>texto</b>
    paragrafos = explicacao.split('\n')
    for paragrafo in paragrafos:
        paragrafo = paragrafo.strip()
        if paragrafo:
            # Substituir **...** por <b>...</b>
            paragrafo_com_negrito = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', paragrafo)
            elements.append(Paragraph(paragrafo_com_negrito, normal_style))
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- 4. CÁLCULO COMPONENTES ----
    elements.append(Paragraph("4. Cálculo Componentes", subtitle_style))
    for grupo, subgrupos in grupos.items():
        elements.append(Paragraph(grupo, bold_style))
        for subgrupo, itens in subgrupos.items():
            elements.append(Paragraph(subgrupo, bold_style))
            for item in itens:
                item_text = f"""
                {item['descricao']} ({item['codigo']}) - {item['quantidade']} {item['unidade']}
                Custo Unitário: R$ {format_currency(item['custo_unitario'])}
                Custo Total: R$ {format_currency(item['custo_total'])}
                Cálculo: {item['explicacao']}
                """
                # Também ajustamos possíveis **negritos** no texto do item
                item_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_text)
                elements.append(Paragraph(item_text, normal_style))
            elements.append(Spacer(1, 0.1 * inch))
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- RESULTADO FINAL ----
    elements.append(Paragraph("Resultado Final", subtitle_style))
    elements.append(Paragraph(f"Custo Total: R$ {format_currency(custo_total)}", bold_style))

    # Se quiser jogar a tabela em uma nova página, descomente a linha abaixo
    # elements.append(PageBreak())

    # ---- TABELA COMPONENTES ----
    elements.append(Spacer(1, 0.3 * inch))  # Espaço antes do título da tabela
    elements.append(Paragraph("Tabela de Componentes", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))  # Espaço controlado antes de iniciar a tabela

    todos_custos = get_all_custos()
    table_data = [["Código", "Descrição", "Unidade", "Custo Unitário"]]
    for custo in todos_custos:
        # Se necessário, também tratamos **texto** da descrição
        desc_tratada = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', custo.descricao)
        table_data.append([
            custo.codigo,
            Paragraph(desc_tratada, normal_style),
            custo.unidade,
            f"R$ {format_currency(custo.valor)}"
        ])
    
    table = Table(table_data, colWidths=[1*inch, 3.5*inch, 1*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(Indenter(left=40))  # 40 pontos ~ 0.56 inch
    elements.append(table)
    elements.append(Indenter(left=-40))  # remove o deslocamento usado anteriormente

    # ---- FINALIZA O PDF ----
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

