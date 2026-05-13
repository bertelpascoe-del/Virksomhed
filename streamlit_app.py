import os
import tempfile
import streamlit as st
import pandas as pd
from backend.financial_analyzer import (
    parse_documents,
    calculate_metrics,
    calculate_score_and_explanation,
    generate_summary_and_recs,
    parse_score_over_time,
)

st.set_page_config(
    page_title="SMB Financial Health Analyzer",
    page_icon="📊",
    layout="wide",
)

st.title("SMB Financial Health Analyzer")
st.markdown(
    "Upload CSV, XLSX or XLS financial reports and get a quick assessment of profitability, liquidity, debt, and cash flow health."
)

uploaded_files = st.file_uploader(
    "Upload financial documents",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True,
)

if uploaded_files:
    if st.button("Analyze uploaded files"):
        with st.spinner("Analyzing files..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                file_paths = []

                for uploaded_file in uploaded_files:
                    out_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(out_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_paths.append(out_path)

                data, parse_warnings = parse_documents(file_paths)

                if data is None:
                    st.error("Could not parse financial data from the uploaded files.")
                    if parse_warnings:
                        st.warning("\n".join(parse_warnings))
                else:
                    metrics, calc_warnings = calculate_metrics(data)
                    score, details, _ = calculate_score_and_explanation(metrics)
                    summary, strengths, weaknesses, recommendations = generate_summary_and_recs(
                        metrics, parse_warnings
                    )
                    score_over_time = parse_score_over_time(file_paths)

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Financial Health Score", score, details["description"])
                    col2.metric("Revenue", f"{data.get('Revenue', 0):,.0f} DKK")
                    col3.metric("Net Profit", f"{metrics.get('NetProfit', 0):,.0f} DKK")

                    st.markdown("### Summary")
                    st.write(summary)

                    st.markdown("### Key Ratios")
                    ratio_df = {
                        "Metric": [
                            "Gross Profit",
                            "Gross Margin (%)",
                            "Net Profit",
                            "Net Margin (%)",
                            "Expense Ratio (%)",
                            "Debt to Revenue (%)",
                            "Current Ratio",
                            "Cash Flow Margin (%)",
                        ],
                        "Value": [
                            f"{metrics.get('GrossProfit', 0):,.0f}",
                            f"{metrics.get('GrossMarginPct', 0):.1f}%",
                            f"{metrics.get('NetProfit', 0):,.0f}",
                            f"{metrics.get('NetMarginPct', 0):.1f}%",
                            f"{metrics.get('ExpenseRatioPct', 0):.1f}%",
                            f"{metrics.get('DebtToRevenueRatioPct', 0):.1f}%",
                            f"{metrics.get('CurrentRatio', 0):.2f}",
                            f"{metrics.get('CashFlowMarginPct', 0):.1f}%",
                        ],
                    }
                    st.table(ratio_df)

                    st.markdown("### Strengths")
                    for item in strengths:
                        st.success(item)

                    st.markdown("### Weaknesses")
                    for item in weaknesses:
                        st.error(item)

                    st.markdown("### Recommendations")
                    for rec in recommendations:
                        st.write(f"**{rec['title']}**: {rec['text']}")

                    if parse_warnings or calc_warnings:
                        st.markdown("### Warnings")
                        for warning in parse_warnings + calc_warnings:
                            st.warning(warning)

                    if score_over_time:
                        st.markdown("### Score Trend Over Time")
                        trend_df = pd.DataFrame(
                            {
                                "Score": [row["score"] for row in score_over_time],
                            },
                            index=[row["period"] for row in score_over_time],
                        )
                        st.line_chart(trend_df)
                        st.write("Showing score development by detected period from the uploaded files.")

else:
    st.info("Upload one or more CSV/XLSX/XLS files to begin analysis.")
