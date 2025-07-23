import streamlit as st
import requests
import json
import tempfile
import pdfplumber

st.title("Compliance Analysis API Streamlit App")

# Get secrets from Streamlit
access_token = st.secrets["ACCESS_TOKEN"]
anon_key = st.secrets["ANON_KEY"]

url = "https://xgpkugvycqikqdixrjst.supabase.co/functions/v1/compliance-analysis"

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
            with pdfplumber.open(tmp_file.name) as pdf:
                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            pdf_text += text + "\n"
                        else:
                            st.warning(f"No extractable text on page {i+1}.")
                    except Exception as page_err:
                        st.warning(f"Could not extract text from page {i+1}: {page_err}")
            if pdf_text.strip():
                st.success("PDF text extracted successfully.")
                st.text_area("Extracted PDF Text", pdf_text, height=200)
            else:
                st.error("No text could be extracted from the PDF. It may be scanned or image-only.")
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {e}")

if st.button("Run Analysis"):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": anon_key,
        "Content-Type": "application/json"
    }
    query_for_api = query
    if pdf_text:
        query_for_api += "\n\n---\nAdditional PDF context:\n" + pdf_text
    payload = {
        "query": query_for_api,
        "analysisType": analysis_type,
        "includePastData": include_past_data
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            st.success(f"Analysis completed: {result.get('success', False)}")
            st.write("Result:", result)
            if "results" in result and "compliance_score" in result["results"]:
                st.metric("Compliance Score", result["results"]["compliance_score"])
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
