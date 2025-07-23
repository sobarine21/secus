import streamlit as st
import requests
import json
import tempfile

from PyPDF2 import PdfReader

st.title("Compliance Analysis API Streamlit App")

# Get secrets from Streamlit
access_token = st.secrets["ACCESS_TOKEN"]
anon_key = st.secrets["ANON_KEY"]

# API endpoint
url = "https://xgpkugvycqikqdixrjst.supabase.co/functions/v1/compliance-analysis"

# Input fields for user
query = st.text_area("Enter your compliance query:", "What are the current ESG reporting requirements?")
analysis_type = st.selectbox("Analysis Type", ["compliance", "risk", "other"], index=0)
include_past_data = st.checkbox("Include Past Data", value=True)

st.write("---")
st.header("PDF Upload (Optional)")
uploaded_pdf = st.file_uploader("Upload a PDF for regulatory or compliance context", type=["pdf"])

pdf_text = ""
if uploaded_pdf is not None:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_pdf.getvalue())
            tmp_file.flush()
            reader = PdfReader(tmp_file.name)
            num_pages = len(reader.pages)
            if num_pages == 0:
                st.error("PDF contains no pages.")
            else:
                for i in range(num_pages):
                    try:
                        text = reader.pages[i].extract_text()
                        if text:
                            pdf_text += text + "\n"
                    except Exception as page_err:
                        st.warning(f"Could not extract text from page {i+1}: {page_err}")
                if pdf_text:
                    st.success("PDF text extracted successfully.")
                    st.text_area("Extracted PDF Text", pdf_text, height=200)
                else:
                    st.error("No text could be extracted from the PDF.")
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {e}")

if st.button("Run Analysis"):
    # Build headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": anon_key,
        "Content-Type": "application/json"
    }

    # Build payload: If PDF text present, append to query
    query_for_api = query
    if pdf_text:
        query_for_api += "\n\n---\nAdditional PDF context:\n" + pdf_text

    payload = {
        "query": query_for_api,
        "analysisType": analysis_type,
        "includePastData": include_past_data
    }

    # Make API request
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            st.success(f"Analysis completed: {result.get('success', False)}")
            st.write("Result:", result)
            if "results" in result and "compliance_score" in result["results"]:
                st.metric("Compliance Score", result["results"]["compliance_score"])
            # Show AI analysis if present
            if "results" in result and "ai_analysis" in result["results"]:
                if result["results"]["ai_analysis"].get("summary"):
                    st.subheader("AI Analysis Summary")
                    st.write(result["results"]["ai_analysis"]["summary"])
                if result["results"]["ai_analysis"].get("full_analysis"):
                    with st.expander("Full AI Analysis"):
                        st.write(result["results"]["ai_analysis"]["full_analysis"])
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Exception occurred: {e}")
