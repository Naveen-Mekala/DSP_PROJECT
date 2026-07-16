import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Prediction Dashboard")

response = requests.get(
    "http://127.0.0.1:8000/past-predictions"
)

if response.status_code == 200:

    df = pd.DataFrame(response.json())

    if len(df) == 0:
        st.warning("No Predictions Found")

    else:

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Predictions",
            len(df)
        )

        col2.metric(
            "Average Prediction",
            round(df["Prediction"].mean(), 2)
        )

        col3.metric(
            "Highest Prediction",
            round(df["Prediction"].max(), 2)
        )

        st.divider()

        st.subheader("Prediction Distribution")

        fig = px.histogram(
            df,
            x="Prediction",
            nbins=20,
            title="Recovery Score Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Sport Type")

        fig2 = px.pie(
            df,
            names="Sport_Type",
            title="Sport Type Distribution"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.subheader("Gender Distribution")

        fig3 = px.bar(
            df,
            x="Gender",
            title="Gender Count"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        st.subheader("Prediction Table")

        st.dataframe(
            df,
            use_container_width=True
        )

else:

    st.error("Could not connect to FastAPI")