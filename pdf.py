from fpdf import FPDF
from datetime import datetime

def limpar_unicode(texto):
    return (texto.replace("✅", "[OK]")
                .replace("❌", "[X]")
                .replace("⚠️", "[!]")
                .replace("🚫", "[X]"))

colunas = [
    "Critério", "MonadScore", "OpenLedger", "Taker", "Parasail", "Rynus.io", "Public AI", "Uplink", "Kaisar",
    "NodePay", "Dawn Network", "3DOS", "Bless", "Gradient", "Multisync", "Stork", "Toggle", "BlockMesh",
    "Teneo", "Depined", "Kleo Network", "NodeGo"
]

dados = [
    ["Base tecnológica", "Rede Monad (L1)", "Blockchain própria", "Multi-chain DeFi", "Multi-chain DePIN", "Blockchain modular",
     "AI descentralizada", "Rede P2P IoT", "Infra DePIN", "DeFi para nodos", "Internet descentralizada", "Armazenamento DePIN",
     "Dados pessoais", "Dados IoT", "Gestão nodos IoT", "Gestão nodos IoT", "Mesh wireless", "Coordenação IoT",
     "Infraestrutura DePIN", "Coordenação blockchain", "Computação descentralizada", "Blockchain com oráculos"],
    ["Proposta", "Reputação via DePIN", "IA com dados verificáveis", "Liquidez NFT", "Garantias DePIN", "Coordenação DePIN",
     "Dados para IA pública", "Conectividade wireless", "Serviços DePIN", "Finanças para nodos", "Banda larga descentralizada",
     "Armazenamento descentralizado", "Dados pessoais", "Coordenação IoT", "Gestão IoT", "Coordenação IoT", "Rede mesh",
     "Gestão nodos IoT", "Infraestrutura e monetização DePIN", "Coordenação de nodos", "Computação compartilhada",
     "Infraestrutura DePIN com dados off-chain"],
    ["Equipe", "❌ Anônima", "✅ Experiente", "✅ Identificada", "✅ Identificada", "✅ Pública", "✅ Pública",
     "✅ Pública", "✅ Pública", "✅ Pública", "✅ Identificada", "✅ Pública", "✅ Pública", "✅ Pública",
     "✅ Pública", "✅ Pública", "✅ Pública", "✅ Pública", "✅ Pública", "⚠️ Pouco transparente",
     "✅ Identificada", "⚠️ Pouco transparente"],
    ["Investidores", "❌ Não divulgados", "✅ Polychain etc", "✅ Electric Capital etc", "✅ Protocol Labs etc",
     "✅ Parcerias estratégicas", "✅ Parcerias em AI", "✅ Parcerias telecom", "✅ Infra blockchain",
     "✅ Investidores públicos", "✅ Andrena", "❌ Não divulgados", "✅ M31 Capital, NGC, Chorus One, etc.",
     "✅ Multicoin, Pantera, Sequoia, etc.", "❌ Não divulgados", "✅ Faction VC, Wintermute, etc.",
     "❌ Não divulgados", "✅ Polychain Capital", "✅ RockawayX, Certik, etc.", "✅ Hash Capital",
     "✅ Parcerias estratégicas", "✅ETHDesign, Hash Capital"],
    ["Auditoria"] + ["❌ Nenhuma"] * 22,
    ["Código aberto", "❌ Não público", "✅ Open-source", "❌ Não público", "❌ Não público", "❌ Não público",
     "❌ Não público", "❌ Não público", "❌ Não público", "✅ Público", "❌ Não público", "❌ Não público",
     "❌ Não público", "❌ Não público", "❌ Não público", "❌ Não público", "❌ Não público", "❌ Não público",
     "❌ Não público", "⚠️ Não disponível", "❌ Não público", "❌ Não público"],
    ["Token", "❌ Não lançado", "❌ Não lançado", "✅ TKR", "❌ Não lançado", "❌ Não lançado", "❌ Não lançado",
     "❌ Não lançado", "❌ Não lançado", "✅ $NPAY", "❌ Não lançado", "❌ Não lançado", "❌ Não lançado",
     "❌ Não lançado", "❌ Não lançado", "❌ Não lançado", "❌ Não lançado", "❌ Não lançado", "❌ Não lançado",
     "❌ Não lançado", "❌ Não lançado", ""],
    ["Transparência", "❌ Baixa", "✅ Alta", "✅ Boa", "✅ Boa", "✅ Boa", "✅ Boa", "✅ Boa", "✅ Boa",
     "✅ Boa", "✅ Boa", "✅ Boa", "✅ Boa", "✅ Boa", "✅ Boa", "✅ Boa", "✅ Boa", "✅ Boa",
     "✅ Boa", "⚠️ Baixa", "✅ Boa", ""],
    ["Comunidade", "⚠️ Ativa, c/ dúvidas", "✅ Engajada", "✅ Ativa", "✅ Engajada", "✅ Ativa", "✅ Ativa",
     "✅ Ativa", "✅ Ativa", "✅ Ativa", "✅ Ativa", "✅ Ativa", "✅ Ativa", "✅ Ativa", "✅ Ativa",
     "✅ Ativa", "✅ Ativa", "✅ Ativa", "✅ Ativa", "⚠️ Feedback negativo", "✅ Engajada", ""],
    ["Risco de scam", "⚠️ Médio", "⚠️ Médio", "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo",
     "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo",
     "⚠️ Baixo", "⚠️ Baixo", "⚠️ Baixo", "⚠️ Alto", "⚠️ Baixo", "⚠️ Alto "],
    ["Recomendação", "⚠️ Cautela", "✅ Acompanhar", "✅ Potencial", "✅ Promissor", "✅ Acompanhar",
     "✅ Interessante", "✅ Acompanhar", "✅ Acompanhar", "✅ Sólido", "✅ Promissor", "⚠️ Monitorar",
     "✅ Promissora", "✅ Promissora", "⚠️ Monitorar", "✅ Promissora", "⚠️ Monitorar", "✅ Promissora",
     "✅ Promissora", "⚠️ Evitar", "✅ Promissora", "⚠️ Evitar (com base nos relatos da comunidade e postura geral do projeto)"],
    ["Status atual", "Em desenvolvimento", "Em progresso", "Token lançado", "Em desenvolvimento", "Em desenvolvimento",
     "Em desenvolvimento", "Em desenvolvimento", "Em desenvolvimento", "Token lançado", "Em desenvolvimento",
     "Em desenvolvimento", "Em desenvolvimento", "Em desenvolvimento", "Em desenvolvimento", "Em desenvolvimento",
     "Em desenvolvimento", "Em desenvolvimento", "Em desenvolvimento", "Site suspeito", "Em desenvolvimento", "Em desenvolvimento (mas com site considerado suspeito e baixa interação legítima)"]
]

dados = [[limpar_unicode(c) for c in linha] for linha in dados]

pdf = FPDF(orientation='L', unit='mm', format='A3')

# Dividir as colunas em 2 blocos
colunas_1 = colunas[:11]                 # primeiras 11 colunas (0 a 10)
colunas_2 = [colunas[0]] + colunas[11:]  # "Critério" + restantes (11 até o fim)

col_width = 30

def add_tabela(pdf, colunas_parte, dados, col_width):
    pdf.set_font("Arial", 'B', 6)
    for col in colunas_parte:
        pdf.cell(col_width, 8, col, border=1, align='C')
    pdf.ln()
    
    pdf.set_font("Arial", '', 6)
    for linha in dados:
        for col in colunas_parte:
            idx = colunas.index(col)  # pegar índice original da coluna
            pdf.cell(col_width, 8, linha[idx], border=1)
        pdf.ln()

# Página 1
pdf.add_page()
pdf.set_font("Arial", 'B', 14)
pdf.cell(0, 10, "Panorama Consolidado de Projetos DePIN - Maio 2025 (Parte 1)", ln=True, align='C')
pdf.set_font("Arial", '', 10)
pdf.cell(0, 10, f"Atualizado em: {datetime.today().strftime('%d/%m/%Y')}", ln=True, align='C')
pdf.ln(5)
add_tabela(pdf, colunas_1, dados, col_width)

# Página 2
pdf.add_page()
pdf.set_font("Arial", 'B', 14)
pdf.cell(0, 10, "Panorama Consolidado de Projetos DePIN - Maio 2025 (Parte 2)", ln=True, align='C')
pdf.set_font("Arial", '', 10)
pdf.cell(0, 10, f"Atualizado em: {datetime.today().strftime('%d/%m/%Y')}", ln=True, align='C')
pdf.ln(5)
add_tabela(pdf, colunas_2, dados, col_width)

pdf.output("Tabela_DePIN_2paginas_A3_Maio2025.pdf")