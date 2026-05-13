import streamlit as st
import pandas as pd
import tempfile
import os
from pathlib import Path
import financial_analyzer as fa
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Finanshjælper", layout="wide")

st.title("📊 Finanshjælper")
st.markdown("**Analyser din virksomheds finansielle sundhed**")

st.info(
    "⚠️ Disclaimer: Dette værktøj giver kun en estimeret finansiel analyse baseret på uploadede data. "
    "Det bør ikke betragtes som professionel finansiel, juridisk eller regnskabsmæssig rådgivning."
)

st.markdown("---")

st.subheader("📁 Upload dine finansielle data")

uploaded_files = st.file_uploader(
    "Vælg CSV, XLSX eller XLS-filer (maks 5 filer, 100 MB i alt)",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True,
)

if uploaded_files:
    total_size = sum(file.size for file in uploaded_files)
    max_size_mb = 100
    max_files = 5

    if len(uploaded_files) > max_files:
        st.error(f"❌ Du kan maksimalt uploade {max_files} filer. Du har uploadet {len(uploaded_files)}.")
    elif total_size > max_size_mb * 1024 * 1024:
        st.error(f"❌ Samlet filstørrelse må ikke overstige {max_size_mb} MB. Du har uploadet {total_size / (1024 * 1024):.2f} MB.")
    else:
        st.success(f"✅ {len(uploaded_files)} fil(er) uploadet. Samlet størrelse: {total_size / (1024 * 1024):.2f} MB")

        temp_paths = []
        try:
            for uploaded_file in uploaded_files:
                suffix = Path(uploaded_file.name).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    temp_paths.append(tmp_file.name)

            with st.spinner("Analyserer data..."):
                parsed_data = fa.parse_documents(temp_paths)

                if parsed_data["warnings"]:
                    st.warning("⚠️ **Advarsler under dataindlæsning:**")
                    for warning in parsed_data["warnings"]:
                        st.write(f"• {warning}")

                if parsed_data["error"]:
                    st.error(f"❌ Fejl: {parsed_data['error']}")
                else:
                    df = parsed_data["data"]

                    metrics = fa.calculate_metrics(df)
                    score, explanation = fa.calculate_score_and_explanation(metrics)
                    summary, recommendations = fa.generate_summary_and_recs(metrics, score)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Financial Health Score", f"{score}/100")
                    with col2:
                        st.metric("Score-vurdering", explanation)
                    with col3:
                        status_color = "🟢" if score >= 75 else "🟡" if score >= 60 else "🔴"
                        st.metric("Status", status_color)

                    st.markdown("---")

                    st.subheading("📈 Finansiel opsummering")
                    st.write(summary)

                    st.markdown("---")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheading("✅ Styrker")
                        for strength in recommendations.get("strengths", []):
                            st.write(f"• {strength}")

                    with col2:
                        st.subheading("⚠️ Svagheder & Risici")
                        for weakness in recommendations.get("weaknesses", []):
                            st.write(f"• {weakness}")

                    st.markdown("---")

                    st.subheading("💡 Anbefalinger")
                    for i, rec in enumerate(recommendations.get("recommendations", []), 1):
                        st.write(f"{i}. {rec}")

                    st.markdown("---")

                    st.subheading("📊 Nøgletal")
                    metrics_cols = st.columns(3)
                    metric_items = [
                        ("Profit Margin", f"{metrics.get('profit_margin', 0):.1f}%"),
                        ("Expense Ratio", f"{metrics.get('expense_ratio', 0):.1f}%"),
                        ("Debt/Revenue", f"{metrics.get('debt_to_revenue', 0):.1f}%"),
                        ("Current Ratio", f"{metrics.get('current_ratio', 0):.2f}"),
                        ("Cash Flow Margin", f"{metrics.get('cash_flow_margin', 0):.1f}%"),
                        ("ROA", f"{metrics.get('roa', 0):.1f}%"),
                    ]

                    for idx, (label, value) in enumerate(metric_items):
                        with metrics_cols[idx % 3]:
                            st.metric(label, value)

                    st.markdown("---")

                    st.subheading("📉 Grafer")

                    col_chart1, col_chart2 = st.columns(2)

                    with col_chart1:
                        st.write("**Finansielle hovedtal**")
                        chart_data = {
                            "Revenue": metrics.get("revenue", 0),
                            "Expenses": metrics.get("expenses", 0),
                            "Debt": metrics.get("debt", 0),
                            "Assets": metrics.get("assets", 0),
                        }
                        fig_bar = go.Figure(
                            data=[go.Bar(x=list(chart_data.keys()), y=list(chart_data.values()), marker_color="steelblue")]
                        )
                        fig_bar.update_layout(
                            title="Vigtigste finansielle tal",
                            xaxis_title="",
                            yaxis_title="Beløb (DKK)",
                            height=400,
                            showlegend=False,
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)

                    with col_chart2:
                        st.write("**Score-fordeling**")
                        scores = {
                            "Profitability": score * 0.30,
                            "Expense Control": score * 0.20,
                            "Debt Risk": score * 0.20,
                            "Liquidity": score * 0.15,
                            "Cash Flow": score * 0.15,
                        }
                        fig_pie = go.Figure(data=[go.Pie(labels=list(scores.keys()), values=list(scores.values()))])
                        fig_pie.update_layout(title="Score-fordeling", height=400)
                        st.plotly_chart(fig_pie, use_container_width=True)

                    score_over_time = fa.parse_score_over_time(temp_paths)
                    if score_over_time and len(score_over_time) > 1:
                        st.markdown("---")
                        st.subheading("📈 Score over tid")
                        fig_line = px.line(
                            x=list(range(len(score_over_time))),
                            y=score_over_time,
                            markers=True,
                            title="Financial Health Score over tid",
                            labels={"x": "Periode", "y": "Score"},
                        )
                        fig_line.update_layout(height=400)
                        st.plotly_chart(fig_line, use_container_width=True)

        finally:
            for temp_path in temp_paths:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception as e:
                    st.warning(f"Kunne ikke slette midlertidig fil: {e}")

else:
    st.info("👉 Upload CSV, XLSX eller XLS-filer for at starte analysen")
    st.markdown(
        """
    ### Eksempel på filformat:
    | Måned | Omsætning | Vareforbrug | Omkostninger | Aktiver | Passiver | Gæld |
    |-------|-----------|-------------|--------------|---------|----------|------|
    | Jan-23 | 50000 | 20000 | 30000 | 300000 | 100000 | 50000 |
    | Feb-23 | 52000 | 21000 | 31000 | 310000 | 105000 | 52000 |
    """
    )