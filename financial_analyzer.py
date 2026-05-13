def parse_documents(uploaded_files):
    import pandas as pd
    from io import BytesIO

    data_frames = []
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, sheet_name=None)
            df = pd.concat(df.values())  # Concatenate all sheets into one DataFrame
        else:
            continue
        data_frames.append(df)
    
    return pd.concat(data_frames, ignore_index=True)

def calculate_metrics(df):
    metrics = {}
    metrics['revenue'] = df['Omsætning'].sum()
    metrics['cogs'] = df['Vareforbrug'].sum()
    metrics['expenses'] = df['Omkostninger'].sum()
    metrics['assets'] = df['Aktiver'].mean()
    metrics['liabilities'] = df['Passiver'].mean()
    metrics['debt'] = df['Gæld'].mean()
    metrics['liquidity'] = df['Likviditet'].mean()
    return metrics

def calculate_score_and_explanation(metrics):
    score = 0
    explanations = []

    # Profitability
    net_margin = (metrics['revenue'] - metrics['expenses']) / metrics['revenue'] * 100 if metrics['revenue'] > 0 else 0
    if net_margin >= 20:
        score += 30
        explanations.append("Excellent profitability")
    elif net_margin >= 10:
        score += 20
        explanations.append("Good profitability")
    elif net_margin >= 0:
        score += 10
        explanations.append("Break-even profitability")
    
    # Expense Control
    expense_ratio = metrics['expenses'] / metrics['revenue'] * 100 if metrics['revenue'] > 0 else 0
    if expense_ratio <= 50:
        score += 20
        explanations.append("Excellent expense control")
    elif expense_ratio <= 80:
        score += 12.5
        explanations.append("Moderate expense control")
    
    # Debt Risk
    debt_ratio = metrics['debt'] / metrics['revenue'] * 100 if metrics['revenue'] > 0 else 0
    if debt_ratio <= 20:
        score += 20
        explanations.append("Low debt risk")
    elif debt_ratio <= 50:
        score += 15
        explanations.append("Moderate debt risk")
    
    # Liquidity
    if metrics['liquidity'] >= 2:
        score += 15
        explanations.append("Strong liquidity")
    elif metrics['liquidity'] >= 1:
        score += 8
        explanations.append("Adequate liquidity")
    
    # Cash Flow
    cash_flow_margin = (metrics['revenue'] - metrics['expenses']) / metrics['revenue'] * 100 if metrics['revenue'] > 0 else 0
    if cash_flow_margin >= 15:
        score += 15
        explanations.append("Strong cash flow")
    elif cash_flow_margin >= 5:
        score += 10
        explanations.append("Adequate cash flow")

    return score, explanations

def generate_summary_and_recs(metrics):
    summary = {
        "Total Revenue": metrics['revenue'],
        "Total Expenses": metrics['expenses'],
        "Average Assets": metrics['assets'],
        "Average Liabilities": metrics['liabilities'],
        "Average Debt": metrics['debt'],
        "Average Liquidity": metrics['liquidity']
    }
    recommendations = []
    
    if metrics['expenses'] > metrics['revenue']:
        recommendations.append("Consider reducing expenses.")
    if metrics['debt'] > metrics['revenue'] * 0.5:
        recommendations.append("Evaluate debt management strategies.")
    
    return summary, recommendations

def parse_score_over_time(df):
    score_over_time = df.groupby('Måned').apply(lambda x: calculate_metrics(x)['revenue']).reset_index()
    return score_over_time