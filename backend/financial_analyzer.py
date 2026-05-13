import pandas as pd
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import re


KEYWORD_MAP = {
    "Revenue": [
        "revenue", "revenues", "sales", "net sales", "gross sales", "income",
        "turnover", "operating income", "total income",

        "omsætning", "omsaetning", "nettoomsætning", "nettoomsaetning",
        "bruttoomsætning", "bruttoomsaetning", "salg", "salgsindtægter",
        "salgsindtaegter", "indtægt", "indtægter", "indtaegt", "indtaegter",
        "driftsindtægter", "driftsindtaegter",

        "omsetning", "salgsinntekter", "inntekter", "driftsinntekter",

        "omsättning", "omsattning", "försäljning", "forsaljning",
        "intäkter", "intakter", "rörelseintäkter", "rorelseintakter",

        "umsatz", "umsatzerlöse", "umsatzerlose", "erlöse", "erlose",
        "einnahmen", "betriebserträge", "betriebsertrage",

        "omzet", "inkomsten", "opbrengsten", "netto omzet",

        "chiffre d'affaires", "chiffre daffaires", "revenus", "ventes",
        "produits",

        "ingresos", "ventas", "facturación", "facturacion",

        "ricavi", "vendite", "fatturato",

        "receita", "receitas", "vendas", "faturamento",

        "przychody", "sprzedaż", "sprzedaz", "obrót", "obrot",

        "liikevaihto", "myynti", "tuotot",

        "tržby", "trzby", "výnosy", "vynosy",
    ],

    "COGS": [
        "cogs", "cost of goods sold", "cost of sales", "direct costs",
        "production cost", "materials", "raw materials", "purchases",

        "vareforbrug", "solgte varers kostpris", "kostpris",
        "direkte omkostninger", "produktionsomkostninger", "materialeforbrug",
        "indkøb", "indkoeb", "varekøb", "varekoeb",

        "varekostnad", "vareforbruk", "direkte kostnader", "innkjøp", "innkjop",

        "varukostnad", "kostnad sålda varor", "kostnad salda varor",
        "direkta kostnader", "inköp", "inkop",

        "wareneinsatz", "materialaufwand", "herstellungskosten",
        "direkte kosten",

        "kostprijs omzet", "inkoopwaarde", "directe kosten", "materiaalkosten",

        "coût des ventes", "cout des ventes", "achats consommés",
        "achats consommes",

        "coste de ventas", "costo de ventas", "compras", "costos directos",

        "costo del venduto", "costi diretti", "materie prime", "acquisti",

        "custo das mercadorias vendidas", "custos diretos", "compras",

        "koszt własny sprzedaży", "koszt wlasny sprzedazy",
        "koszty bezpośrednie", "koszty bezposrednie",

        "myytyjen tuotteiden kulut", "materiaalikulut", "ostot",

        "náklady na prodané zboží", "naklady na prodane zbozi",
        "přímé náklady", "prime naklady",
    ],

    "Expenses": [
        "expenses", "operating expenses", "opex", "costs", "overhead",
        "administrative expenses", "staff costs", "payroll", "wages",
        "salaries", "rent", "utilities",

        "omkostninger", "driftsomkostninger", "administrationsomkostninger",
        "personaleomkostninger", "løn", "loen", "lønninger", "loenninger",
        "udgifter", "faste omkostninger", "variable omkostninger",
        "salgsomkostninger", "administration",

        "kostnader", "driftskostnader", "lønn", "lonn", "utgifter",
        "personalkostnader",

        "kostnader", "rörelsekostnader", "rorelsekostnader", "lön", "lon",

        "kosten", "aufwand", "betriebskosten", "personalkosten",
        "verwaltungsaufwand",

        "bedrijfskosten", "personeelskosten", "loonkosten", "algemene kosten",

        "charges", "dépenses", "depenses", "charges d'exploitation",
        "frais généraux", "frais generaux", "salaires",

        "gastos", "costes", "costos", "gastos operativos",
        "gastos administrativos", "sueldos", "salarios",

        "costi", "spese", "costi operativi", "spese amministrative",

        "despesas", "custos", "despesas operacionais", "salários", "salarios",

        "koszty", "wydatki", "koszty operacyjne", "wynagrodzenia",

        "kulut", "kustannukset", "henkilöstökulut", "henkilostokulut",

        "náklady", "naklady", "provozní náklady", "provozni naklady", "mzdy",
    ],

    "Debt": [
        "debt", "loan", "loans", "borrowings", "bank loan",
        "credit facility", "interest bearing debt",

        "gæld", "gaeld", "lån", "laan", "banklån", "banklaan",
        "kredit", "kassekredit", "rentebærende gæld", "rentebaerende gaeld",

        "gjeld", "lån", "lan", "banklån", "banklan",

        "skuld", "skulder", "lån", "lan", "banklån", "banklan",

        "schulden", "darlehen", "kredit", "bankdarlehen",

        "schuld", "schulden", "lening", "leningen", "banklening",

        "dette", "dettes", "emprunt", "emprunts", "prêt", "pret",

        "deuda", "deudas", "préstamo", "prestamo", "préstamos", "prestamos",

        "debito", "debiti", "prestito", "prestiti", "finanziamenti",

        "dívida", "divida", "dívidas", "dividas", "empréstimo", "emprestimo",

        "dług", "dlug", "długi", "dlugi", "pożyczka", "pozyczka", "kredyt",

        "velka", "lainat", "pankkilaina",

        "dluh", "dluhy", "úvěr", "uver", "půjčka", "pujcka",
    ],

    "Assets": [
        "assets", "current assets", "cash at bank", "bank balance",
        "receivables", "inventory", "stock",

        "aktiver", "omsætningsaktiver", "omsaetningsaktiver",
        "anlægsaktiver", "anlaegsaktiver", "likvider", "bankbeholdning",
        "kasse", "tilgodehavender", "varelager",

        "eiendeler", "omløpsmidler", "omlopsmidler", "anleggsmidler",
        "kontanter", "bank", "fordringer", "varelager",

        "tillgångar", "tillgangar", "omsättningstillgångar",
        "omsattningstillgangar", "kassa", "bank", "kundfordringar", "lager",

        "vermögen", "vermogen", "aktiva", "umlaufvermögen",
        "umlaufvermogen", "anlagevermögen", "anlagevermogen", "forderungen",

        "activa", "bezittingen", "vlottende activa", "vaste activa",
        "debiteuren", "voorraad",

        "actifs", "actif", "actifs courants", "trésorerie", "tresorerie",
        "créances", "creances", "stocks",

        "activos", "activo", "activo corriente", "efectivo",
        "cuentas por cobrar", "inventario",

        "attività", "attivita", "attivo", "attivo corrente",
        "crediti", "magazzino",

        "ativos", "ativo", "ativo circulante", "caixa", "banco",
        "contas a receber", "estoque",

        "aktywa", "aktywa obrotowe", "środki pieniężne",
        "srodki pieniezne", "należności", "naleznosci", "zapasy",

        "varat", "vaihto-omaisuus", "saamiset", "rahavarat",

        "aktiva", "oběžná aktiva", "obezna aktiva", "pohledávky",
        "pohledavky", "zásoby", "zasoby",
    ],

    "Liabilities": [
        "liabilities", "current liabilities", "payables", "accounts payable",

        "passiver", "forpligtelser", "kortfristede forpligtelser",
        "langfristede forpligtelser", "leverandørgæld", "leverandorgaeld",
        "skyldige omkostninger",

        "gjeld", "kortsiktig gjeld", "langsiktig gjeld",
        "leverandørgjeld", "leverandorgjeld", "forpliktelser",

        "skulder", "kortfristiga skulder", "långfristiga skulder",
        "langfristiga skulder", "leverantörsskulder", "leverantorsskulder",

        "verbindlichkeiten", "kurzfristige verbindlichkeiten",
        "langfristige verbindlichkeiten", "passiva",

        "passiva", "verplichtingen", "kortlopende schulden",
        "crediteuren", "te betalen",

        "passifs", "passif", "dettes fournisseurs",
        "passifs courants", "fournisseurs",

        "pasivos", "pasivo", "pasivo corriente", "cuentas por pagar",
        "proveedores",

        "passività", "passivita", "passivo", "debiti verso fornitori",

        "passivos", "passivo", "passivo circulante",
        "contas a pagar", "fornecedores",

        "zobowiązania", "zobowiazania", "pasywa",
        "zobowiązania krótkoterminowe", "zobowiazania krotkoterminowe",

        "velat", "lyhytaikaiset velat", "ostovelat",

        "pasiva", "závazky", "zavazky", "krátkodobé závazky",
        "kratkodobe zavazky",
    ],

    "CashFlow": [
        "cash flow", "cashflow", "operating cash flow", "net cash flow",
        "free cash flow",

        "pengestrøm", "pengestroem", "likviditetsflow", "likviditet",
        "driftslikviditet", "cash flow fra drift", "netto pengestrøm",
        "netto pengestroem",

        "kontantstrøm", "kontantstrom", "likviditet", "kontantflyt",

        "kassaflöde", "kassaflode", "likviditet", "operativt kassaflöde",

        "cashflow", "cash flow", "zahlungsfluss", "liquidität", "liquiditat",

        "kasstroom", "cashflow", "operationele kasstroom",

        "flux de trésorerie", "flux de tresorerie", "cash flow",
        "trésorerie", "tresorerie",

        "flujo de caja", "flujo de efectivo", "cash flow",

        "flusso di cassa", "cash flow", "flussi di cassa",

        "fluxo de caixa", "cash flow", "fluxo de tesouraria",

        "przepływy pieniężne", "przeplywy pieniezne", "cash flow",

        "kassavirta", "rahavirta",

        "peněžní tok", "penezni tok", "cash flow",
    ],
}


def normalize_string(text: str) -> str:
    text = str(text).lower().strip()

    replacements = {
        "æ": "ae", "ø": "oe", "å": "aa",
        "ä": "a", "ö": "o", "ü": "u",
        "é": "e", "è": "e", "ê": "e",
        "á": "a", "à": "a", "â": "a",
        "í": "i", "ì": "i",
        "ó": "o", "ò": "o", "ô": "o",
        "ú": "u", "ù": "u",
        "ç": "c", "ñ": "n", "ß": "ss",
        "ł": "l", "ś": "s", "ż": "z", "ź": "z",
        "ć": "c", "ń": "n", "ř": "r", "č": "c",
        "š": "s", "ž": "z", "ý": "y", "ě": "e",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return re.sub(r"[^a-z0-9]", "", text)


def similarity(a: str, b: str) -> float:
    a = normalize_string(a)
    b = normalize_string(b)

    if not a or not b:
        return 0

    return SequenceMatcher(None, a, b).ratio()


def keyword_score(label: str, keywords: list[str]) -> float:
    label_norm = normalize_string(label)
    best = 0

    for keyword in keywords:
        keyword_norm = normalize_string(keyword)

        if not keyword_norm:
            continue

        if label_norm == keyword_norm:
            best = max(best, 1.2)
        elif keyword_norm in label_norm:
            length_bonus = min(len(keyword_norm) / 20, 0.25)
            best = max(best, 1.0 + length_bonus)
        elif label_norm in keyword_norm and len(label_norm) >= 5:
            best = max(best, 0.9)

        fuzzy = similarity(label_norm, keyword_norm)
        best = max(best, fuzzy)

    return best


def detect_metric_from_label(label: str) -> tuple[str | None, float]:
    best_metric = None
    best_score = 0

    for metric, keywords in KEYWORD_MAP.items():
        score = keyword_score(label, keywords)

        if score > best_score:
            best_metric = metric
            best_score = score

    if best_score >= 0.72:
        return best_metric, best_score

    return None, best_score


def read_file_to_dataframes(path: str) -> Tuple[List[pd.DataFrame], List[str]]:
    warnings = []
    dataframes = []

    try:
        lower_path = path.lower()

        if lower_path.endswith(".csv"):
            dataframes.append(pd.read_csv(path))

        elif lower_path.endswith((".xlsx", ".xls")):
            sheets = pd.read_excel(path, sheet_name=None, header=None)

            for sheet_name, df in sheets.items():
                if df.empty:
                    continue

                dataframes.append(df)

                try:
                    df_header = pd.read_excel(path, sheet_name=sheet_name)
                    if not df_header.empty:
                        dataframes.append(df_header)
                except Exception:
                    pass

        else:
            warnings.append(f"Unsupported file type: {path}")

    except Exception as e:
        warnings.append(f"Error reading {path}: {e}")

    return dataframes, warnings


def extract_from_column_layout(df: pd.DataFrame) -> Tuple[Dict[str, float], List[str]]:
    data = {}
    warnings = []

    for col in df.columns:
        metric, score = detect_metric_from_label(col)

        if metric:
            numeric_col = pd.to_numeric(df[col], errors="coerce")
            value = numeric_col.mean()

            if not pd.isna(value):
                data[metric] = data.get(metric, 0) + float(value)

    return data, warnings


def extract_from_row_layout(df: pd.DataFrame) -> Tuple[Dict[str, float], List[str]]:
    data = {}
    warnings = []

    if df.shape[1] < 2:
        return data, warnings

    for _, row in df.iterrows():
        row_values = list(row.values)

        text_parts = []
        numeric_values = []

        for value in row_values:
            numeric_value = pd.to_numeric(value, errors="coerce")

            if pd.isna(numeric_value):
                if not pd.isna(value):
                    text_parts.append(str(value))
            else:
                numeric_values.append(float(numeric_value))

        if not text_parts or not numeric_values:
            continue

        label = " ".join(text_parts)
        metric, score = detect_metric_from_label(label)

        if metric:
            value = numeric_values[-1]
            data[metric] = data.get(metric, 0) + value

    return data, warnings


def parse_documents(file_paths: List[str]) -> Tuple[Dict[str, float] | None, List[str]]:
    aggregated_data = {}
    warnings = []

    for path in file_paths:
        dataframes, read_warnings = read_file_to_dataframes(path)
        warnings.extend(read_warnings)

        for df in dataframes:
            if df.empty:
                continue

            column_data, column_warnings = extract_from_column_layout(df)
            row_data, row_warnings = extract_from_row_layout(df)

            warnings.extend(column_warnings)
            warnings.extend(row_warnings)

            for source in [column_data, row_data]:
                for key, value in source.items():
                    aggregated_data[key] = aggregated_data.get(key, 0) + value

    if not aggregated_data:
        warnings.append(
            "No recognizable financial fields were detected. Try clearer labels such as omsætning, omkostninger, aktiver, passiver, gæld, or cash flow."
        )
        return None, warnings

    return aggregated_data, warnings


def calculate_metrics(data: Dict[str, float]) -> Tuple[Dict[str, float], List[str]]:
    rev = data.get("Revenue", 0)
    cogs = data.get("COGS", 0)
    exp = data.get("Expenses", 0)
    debt = data.get("Debt", 0)
    assets = data.get("Assets", 0)
    liab = data.get("Liabilities", 0)
    cf = data.get("CashFlow", 0)

    warnings = []

    metrics = {
        "GrossProfit": rev - cogs,
        "GrossMarginPct": ((rev - cogs) / rev * 100) if rev else 0,
        "NetProfit": rev - cogs - exp,
        "NetMarginPct": ((rev - cogs - exp) / rev * 100) if rev else 0,
        "ExpenseRatioPct": (exp / rev * 100) if rev else 0,
        "DebtToRevenueRatioPct": (debt / rev * 100) if rev else 0,
        "CurrentRatio": (assets / liab) if liab > 0 else 0,
        "CashFlowMarginPct": (cf / rev * 100) if rev else 0,
    }

    if rev == 0:
        warnings.append("Revenue/omsætning was not detected or is zero. Analysis may be unreliable.")

    if liab == 0 and assets > 0:
        warnings.append("Liabilities/passiver were not detected. Current ratio may be inaccurate.")

    return metrics, warnings


def calculate_score_and_explanation(metrics: Dict[str, float]) -> Tuple[int, dict, list]:
    nm = metrics.get("NetMarginPct", -100)
    er = metrics.get("ExpenseRatioPct", 100)
    dr = metrics.get("DebtToRevenueRatioPct", 100)
    cr = metrics.get("CurrentRatio", 0)
    cfm = metrics.get("CashFlowMarginPct", -100)

    profit = 30 if nm >= 20 else 20 if nm >= 10 else 10 if nm >= 0 else 0
    expense = 20 if er <= 50 else 12.5 if er <= 80 else 0
    debt = 20 if dr <= 20 else 15 if dr <= 50 else 5 if dr <= 100 else 0
    liquidity = 15 if cr >= 2 else 8 if cr >= 1 else 0
    cash = 15 if cfm >= 15 else 10 if cfm >= 5 else 5 if cfm >= 0 else 0

    score = max(1, min(100, int(profit + expense + debt + liquidity + cash)))

    if score >= 90:
        desc = "Excellent financial health"
    elif score >= 75:
        desc = "Good financial health"
    elif score >= 60:
        desc = "Fair but needs attention"
    elif score >= 40:
        desc = "Weak financial health"
    else:
        desc = "High financial risk"

    return score, {"description": desc}, []


def generate_summary_and_recs(metrics: Dict[str, float], warnings: List[str]) -> Tuple[str, list, list, list]:
    nm = metrics.get("NetMarginPct", 0)
    er = metrics.get("ExpenseRatioPct", 0)
    dr = metrics.get("DebtToRevenueRatioPct", 0)
    cr = metrics.get("CurrentRatio", 0)
    cfm = metrics.get("CashFlowMarginPct", 0)

    summary = (
        f"Net margin is {nm:.1f}%, expense ratio is {er:.1f}%, "
        f"debt-to-revenue is {dr:.1f}%, current ratio is {cr:.1f}, "
        f"and cash flow margin is {cfm:.1f}%."
    )

    strengths = []
    weaknesses = []
    recs = []

    if nm >= 20:
        strengths.append("Strong profitability: net margin is above 20%.")
    if cr >= 1.5:
        strengths.append("Good liquidity: current ratio is healthy.")
    if cfm >= 10:
        strengths.append("Strong cash generation.")

    if nm < 0:
        weaknesses.append("Negative net margin.")
        recs.append({
            "title": "Restore profitability",
            "text": "Review pricing, COGS/vareforbrug, and operating expenses/omkostninger."
        })

    if dr > 50:
        weaknesses.append("Debt is high compared with revenue.")
        recs.append({
            "title": "Manage debt load",
            "text": "Review loans/gæld and consider refinancing or repayment planning."
        })

    if er > 70:
        weaknesses.append("Expense ratio is high.")
        recs.append({
            "title": "Audit overhead",
            "text": "Review recurring expenses, supplier contracts, payroll, and non-essential costs."
        })

    if cr < 1:
        weaknesses.append("Liquidity is weak.")
        recs.append({
            "title": "Improve cash flow",
            "text": "Improve collections and negotiate supplier payment terms."
        })

    if not strengths:
        strengths.append("No major strength detected from the available basic ratios.")

    if not weaknesses:
        weaknesses.append("No critical weakness detected from the basic ratio analysis.")

    if not recs:
        recs.append({
            "title": "Maintain financial discipline",
            "text": "Monitor margins, expenses, debt, and cash flow monthly."
        })

    return summary, strengths, weaknesses, recs

def detect_period_column(df: pd.DataFrame):
    """
    Detects a date/month/period column for score-over-time charts.
    Supports English and Danish labels.
    """
    period_keywords = [
        "date", "month", "period", "year", "quarter",
        "dato", "måned", "maaned", "periode", "år", "aar", "kvartal"
    ]

    for col in df.columns:
        col_norm = normalize_string(col)
        for keyword in period_keywords:
            if normalize_string(keyword) in col_norm:
                return col

    return None


def parse_score_over_time(file_paths: List[str]) -> List[dict]:
    """
    Attempts to calculate a financial health score per row/period.
    Works best for column-based files where each row is a month, quarter, or year.
    """
    score_over_time = []

    for path in file_paths:
        dataframes, _ = read_file_to_dataframes(path)

        for df in dataframes:
            if df.empty:
                continue

            period_col = detect_period_column(df)

            # Map detected financial columns to internal metric names
            detected_cols = {}

            for col in df.columns:
                metric, confidence = detect_metric_from_label(col)

                if metric and metric not in detected_cols:
                    detected_cols[metric] = col

            # Need at least revenue to create meaningful trend scores
            if "Revenue" not in detected_cols:
                continue

            for index, row in df.iterrows():
                period_label = str(row[period_col]) if period_col is not None else f"Row {index + 1}"

                row_data = {
                    "Revenue": 0,
                    "COGS": 0,
                    "Expenses": 0,
                    "Debt": 0,
                    "Assets": 0,
                    "Liabilities": 0,
                    "CashFlow": 0,
                }

                for metric, col in detected_cols.items():
                    value = pd.to_numeric(row[col], errors="coerce")

                    if not pd.isna(value):
                        row_data[metric] = float(value)

                metrics, _ = calculate_metrics(row_data)
                score, details, _ = calculate_score_and_explanation(metrics)

                score_over_time.append({
                    "period": period_label,
                    "score": score,
                    "description": details["description"],
                    "revenue": row_data.get("Revenue", 0),
                    "netProfit": metrics.get("NetProfit", 0),
                    "netMarginPct": metrics.get("NetMarginPct", 0),
                })

    return score_over_time