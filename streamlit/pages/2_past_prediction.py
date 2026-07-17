import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Past Predictions",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Past Predictions")

st.markdown("---")

try:
    response = requests.get(
        "http://fastapi:8000/past-predictions"
    )

    if response.status_code == 200:

        data = response.json()

        if len(data) == 0:
            st.warning("No predictions found.")

        else:
            df = pd.DataFrame(data)

            st.success(f"{len(df)} Predictions Found")

            st.dataframe(
                df,
                use_container_width=True
            )

    else:
        st.error("Could not fetch predictions.")
        st.write(response.text)

except Exception as e:
    st.error("Could not connect to FastAPI.")
    st.exception(e)