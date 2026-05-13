import streamlit as st
import pandas as pd
import tempfile
import financial_analyzer as fa

# Title of the app
st.title("Finansiel Analyse Værktøj")

# Disclaimer
st.markdown("**Disclaimer:** Dette værktøj giver kun en estimeret finansiel analyse baseret på uploadede data. Det bør ikke betragtes som professionel finansiel, juridisk eller regnskabsmæssig rådgivning.")

# File uploader
uploaded_files = st.file_uploader("Upload CSV, XLSX eller XLS filer", type=["csv", "xlsx", "xls"], accept_multiple_files=True)

# Check if files are uploaded
if uploaded_files:
    if len(uploaded_files) > 5:
        st.error("Maksimalt 5 filer kan uploades ad gangen.")
    else:
        total_size = sum(file.size for file in uploaded_files)
        if total_size > 100 * 1024 * 1024:  # 100 MB
            st.error("Den samlede uploadstørrelse må ikke overstige 100 MB.")
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                data_frames = []
                for uploaded_file in uploaded_files:
                    file_path = f"{tmpdirname}/{uploaded_file.name}"
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    df = fa.parse_documents(file_path)
                    data_frames.append(df)

                # Combine data frames if necessary
                combined_df = pd.concat(data_frames, ignore_index=True)

                # Perform financial analysis
                score, explanation = fa.calculate_score_and_explanation(combined_df)
                summary, recommendations = fa.generate_summary_and_recs(combined_df)

                # Display results
                st.subheader("Finansiel Sundhed Score")
                st.write(f"Score: {score} ({explanation})")

                st.subheader("Finansiel Opsummering")
                st.write(summary)

                st.subheader("Anbefalinger")
                st.write(recommendations)

                # Display charts
                if 'score_over_time' in combined_df.columns:
                    score_over_time = fa.parse_score_over_time(combined_df)
                    st.line_chart(score_over_time)

                # Display bar chart for financial metrics
                metrics = fa.calculate_metrics(combined_df)
                st.bar_chart(metrics)

                # Display strengths and weaknesses
                strengths, weaknesses = fa.analyze_strengths_and_weaknesses(combined_df)
                st.subheader("Styrker")
                st.write(strengths)
                st.subheader("Svagheder/Risici")
                st.write(weaknesses)