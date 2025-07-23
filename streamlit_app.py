import streamlit as st
import requests
import json

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

if st.button("Run Analysis"):
    # Build headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": anon_key,
        "Content-Type": "application/json"
    }

    # Build payload
    payload = {
        "query": query,
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
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Exception occurred: {e}")
