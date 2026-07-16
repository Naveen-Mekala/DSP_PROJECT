import streamlit as st
import requests

st.set_page_config(
    page_title="Batch Prediction",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Batch Prediction")

st.write("Upload a CSV file to predict recovery scores for all athletes.")

uploaded_file = st.file_uploader(
    "Choose CSV File",
    type=["csv"]
)

if uploaded_file is not None:

    st.success("CSV Uploaded Successfully!")

    if st.button("🚀 Run Batch Prediction"):

        with st.spinner("Predicting..."):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file,
                    "text/csv"
                )
            }

            response = requests.post(
                "http://127.0.0.1:8000/batch-predict",
                files=files
            )

            if response.status_code == 200:

                st.success("Batch Prediction Completed!")

                st.download_button(
                    label="⬇ Download Prediction CSV",
                    data=response.content,
                    file_name="batch_predictions.csv",
                    mime="text/csv"
                )

            else:

                st.error("Prediction Failed")

                st.write(response.text)