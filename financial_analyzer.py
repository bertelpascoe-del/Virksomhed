import pandas as pd
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

FINANCIAL_TERMS = {
    "revenue": [
        "revenue", "omsætning", "omsetning", "inkomst", "salg", "sales", "turnover",
        "chiffre d'affaires", "ventas", "ricavi", "receita", "opbrengsten", "przychody",
        "tulot", "tržby", "omzet", "umsatz", "revenu"
    ],
    "cogs": [
        "cogs", "cost of goods sold", "vareforbrug", "varekost", "kostnad", "cost of sales",
        "coût des marchandises", "coste de mercancías", "costo delle merci", "custo das mercadorias",
        "kostprijs", "koszt sprzedanych towarów", "tavaraiden hankintahinta", "cena prodaných zboží",
        "warenkost"
    ],
    "expenses": [
        "expenses", "omkostninger", "kostnader", "utgifter", "operating expenses",
        "frais", "gastos", "spese", "despesas", "bedrijfskosten", "wydatki", "kulut", "náklady",
        "ausgaben", "kosten"
    ],
    "debt": [
        "debt", "gæld", "gjeld", "skuld", "lån", "långivare", "dépôt", "deuda", "debito",
        "débito", "schuld", "dlug", "velka", "schulden"
    ],
    "assets": [
        "assets", "aktiver", "aktiva", "formue", "eiendom", "actif", "activos", "attivo",
        "ativos", "vermogen", "aktywa", "varat", "majetek", "vermögen"
    ],
    "liabilities": [
        "liabilities", "passiver", "forpligtelser", "skulder", "passif", "pasivos",
        "passività", "passivos", "verplichtingen", "zobowiązania", "velat", "závazky", "verbindlichkeiten"
    ],
    "cashflow": [
        "cash flow", "pengestrøm", "pengeflyt", "likviditet", "kontantflöde", "flux de trésorerie",
        "flujo de caja", "flusso di cassa", "fluxo de caixa", "kasstroom", "przepływ gotówki",
        "kassavirta", "peněžní tok", "geldfluss", "cash"
    ],
}

def normalize_text(text):
    """Normaliserer tekst for fuzzy matching."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = ''.join(c if c.isalnum() else '' for c in text)
    return text

def find_matching_term(column_name, term_category):
    """Finder matching finansielt term via fuzzy matching."""
    normalized_col = normalize_text(column_name)

    best_match = None
    best_ratio = 0

    for term in FINANCIAL_TERMS.get(term_category, []):
        normalized_term = normalize_text(term)
        ratio = SequenceMatcher(None, normalized_col, normalized_term).ratio()

        if ratio > best_ratio:
            best_ratio = ratio
            best_match = term

    return best_match if best_ratio >= 0.6 else None

def parse_documents(file_paths):
    """Læser CSV, XLSX og XLS-filer fra filstier."""
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    combined_df = None
    warnings = []
    error = None

    try:
        for file_path in file_paths:
            try:
                file_path_str = str(file_path).lower()

                if file_path_str.endswith(".csv"):
                    df = pd.read_csv(file_path)
                elif file_path_str.endswith((".xlsx", ".xls")):
                    excel_file = pd.ExcelFile(file_path)
                    if len(excel_file.sheet_names) > 0:
                        df = pd.read_excel(file_path, sheet_name=0)
                    else:
                        warnings.append(f"Ingen sheets fundet i {Path(file_path).name}")
                        continue
                else:
                    warnings.append(f"Filtype ikke understøttet: {Path(file_path).name}")
                    continue

                if df is None or df.empty:
                    warnings.append(f"Filen {Path(file_path).name} er tom")
                    continue

                if combined_df is None:
                    combined_df = df
                else:
                    combined_df = pd.concat([combined_df, df], ignore_index=True)

            except Exception as e:
                warnings.append(f"Fejl ved læsning af {Path(file_path).name}: {str(e)}")
                continue

        if combined_df is None or combined_df.empty:
            error = "Ingen gyldige data fundet i uploadede filer"
            combined_df = pd.DataFrame()

    except Exception as e:
        error = f"Fejl ved procesering af filer: {str(e)}"
        combined_df = pd.DataFrame()

    return {
        "data": combined_df,
        "warnings": warnings,
        "error": error,
    }

def calculate_metrics(df):
    """Beregner finansielle nøgletal fra DataFrame."""
    metrics = {
        "revenue": 0,
        "cogs": 0,
        "expenses": 0,
        "debt": 0,
        "assets": 0,
        "liabilities": 0,
        "cashflow": 0,
        "profit_margin": 0,
        "expense_ratio": 0,
        "debt_to_revenue": 0,
        "current_ratio": 1,
        "cash_flow_margin": 0,
        "roa": 0,
    }

    if df.empty:
        return metrics

    df.columns = [str(col).strip() for col in df.columns]

    for column in df.columns:
        for term_cat in FINANCIAL_TERMS.keys():
            if find_matching_term(column, term_cat):
                try:
                    numeric_vals = pd.to_numeric(df[column], errors='coerce')
                    values = numeric_vals.dropna()

                    if len(values) > 0:
                        avg_value = values.mean()
                        metrics[term_cat] = max(metrics[term_cat], avg_value)
                except:
                    pass

    if metrics["revenue"] > 0:
        metrics["profit_margin"] = ((metrics["revenue"] - metrics["cogs"] - metrics["expenses"]) / metrics["revenue"]) * 100
        metrics["expense_ratio"] = (metrics["expenses"] / metrics["revenue"]) * 100
        metrics["debt_to_revenue"] = (metrics["debt"] / metrics["revenue"]) * 100
        metrics["cash_flow_margin"] = (metrics["cashflow"] / metrics["revenue"]) * 100

    if metrics["liabilities"] > 0:
        metrics["current_ratio"] = metrics["assets"] / metrics["liabilities"]

    if metrics["assets"] > 0:
        net_income = metrics["revenue"] - metrics["cogs"] - metrics["expenses"]
        metrics["roa"] = (net_income / metrics["assets"]) * 100

    return metrics

def calculate_score_and_explanation(metrics):
    """Beregner Financial Health Score baseret på metrics."""
    score = 0

    profit_margin = metrics.get("profit_margin", 0)
    if profit_margin >= 20:
        score += 30
    elif profit_margin >= 10:
        score += 20
    elif profit_margin >= 0:
        score += 10

    expense_ratio = metrics.get("expense_ratio", 0)
    if expense_ratio <= 50:
        score += 20
    elif expense_ratio <= 80:
        score += 12.5

    debt_to_revenue = metrics.get("debt_to_revenue", 0)
    if debt_to_revenue <= 20:
        score += 20
    elif debt_to_revenue <= 50:
        score += 15
    elif debt_to_revenue <= 100:
        score += 5

    current_ratio = metrics.get("current_ratio", 0)
    if current_ratio >= 2:
        score += 15
    elif current_ratio >= 1:
        score += 8

    cash_flow_margin = metrics.get("cash_flow_margin", 0)
    if cash_flow_margin >= 15:
        score += 15
    elif cash_flow_margin >= 5:
        score += 10
    elif cash_flow_margin >= 0:
        score += 5

    score = min(100, max(1, int(score)))

    if score >= 90:
        explanation = "Excellent"
    elif score >= 75:
        explanation = "Good"
    elif score >= 60:
        explanation = "Fair"
    elif score >= 40:
        explanation = "Weak"
    else:
        explanation = "High Risk"

    return score, explanation

def generate_summary_and_recs(metrics, score):
    """Genererer finansiel opsummering og anbefalinger."""
    revenue = metrics.get("revenue", 0)
    profit_margin = metrics.get("profit_margin", 0)
    expense_ratio = metrics.get("expense_ratio", 0)
    debt_to_revenue = metrics.get("debt_to_revenue", 0)
    current_ratio = metrics.get("current_ratio", 1)
    cash_flow_margin = metrics.get("cash_flow_margin", 0)

    summary = f"""
Din virksomhed har en omsætning på **{revenue:,.0f} DKK** med en profit margin på **{profit_margin:.1f}%**.
Omkostningsforholdet er **{expense_ratio:.1f}%** og gældsforholdet er **{debt_to_revenue:.1f}%** af omsætningen.
Likviditetsgraden er **{current_ratio:.2f}** og cash flow-marginen er **{cash_flow_margin:.1f}%**.
    """.strip()

    strengths = []
    weaknesses = []
    recommendations = []

    if profit_margin >= 10:
        strengths.append("God rentabilitet med solid profit margin")
    else:
        weaknesses.append("Lav rentabilitet - bør fokusere på indtjening")

    if expense_ratio <= 60:
        strengths.append("Godt omkostningskontrol")
    else:
        weaknesses.append("Høje omkostninger i forhold til omsætning")
        recommendations.append("Analyser og reducer driftsmæssige omkostninger")

    if debt_to_revenue <= 50:
        strengths.append("Acceptabel gældsgrad")
    else:
        weaknesses.append("Høj gæld i forhold til omsætning - øget risiko")
        recommendations.append("Fokuser på gældsnedbringelse eller omsætningsstigning")

    if current_ratio >= 1.5:
        strengths.append("Solid likviditet")
    elif current_ratio < 1:
        weaknesses.append("Potentiel likviditetskrise - kort sigt betalingsudfordringer")
        recommendations.append("Øg likvide midler eller reducer kortfristet gæld")

    if cash_flow_margin >= 5:
        strengths.append("Positiv cash flow margin")
    else:
        weaknesses.append("Svag cash flow - likviditetspressure")
        recommendations.append("Forbedre cash conversion cycle")

    if score >= 75:
        recommendations.append("Fortsæt nuværende strategi og fokuser på vedligeholdelse af økonomisk sundhed")
    elif score >= 60:
        recommendations.append("Implementer forbedringer på identificerede svaghedsområder")
    else:
        recommendations.append("Søg professionel finansiel rådgivning for strategisk turnaround")

    return summary, {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
    }

def parse_score_over_time(file_paths):
    """Analyserer score over tid hvis data indeholder tidsserier."""
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    scores_over_time = []

    try:
        for file_path in file_paths:
            try:
                file_path_str = str(file_path).lower()

                if file_path_str.endswith(".csv"):
                    df = pd.read_csv(file_path)
                elif file_path_str.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(file_path, sheet_name=0)
                else:
                    continue

                if df is None or df.empty:
                    continue

                for idx, row in df.iterrows():
                    row_dict = row.to_dict()
                    metrics = calculate_metrics(pd.DataFrame([row_dict]))
                    score, _ = calculate_score_and_explanation(metrics)
                    scores_over_time.append(score)

            except:
                continue

    except:
        pass

    return scores_over_time