import streamlit as st
import groq
import PyPDF2
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API setup
groq_api_key = os.getenv("GROQ_API_KEY")
client = groq.Client(api_key=groq_api_key)

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_info_from_text(text):
    # This is a placeholder function. In a real-world scenario, you'd use more
    # sophisticated NLP techniques to extract this information accurately.
    prompt = f"""
    Extract the purchasing manager details and scope of work from the following text:
    {text[:1000]}  # Limiting to first 1000 characters for brevity
    
    Format the response as:
    Purchasing Manager: [extracted details]
    Scope of Work: [extracted details]
    """
    
    response = client.chat.completions.create(
        model="llama-3.1",
        messages=[
            {"role": "system", "content": "You are an expert at extracting specific information from text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    
    extracted_info = response.choices[0].message.content
    return extracted_info.split("\n")

def generate_proposal(document_text, disaster_article, yearly_budget, purchasing_manager, scope_of_work):
    prompt = f"""
    Write a proposal based on the following information:
    Document: {document_text[:1000]}  # Limiting to first 1000 characters for brevity
    Disaster Article: {disaster_article[:500]}  # Limiting to first 500 characters for brevity
    Purchasing Manager: {purchasing_manager}
    Scope of Work: {scope_of_work}
    Yearly Budget: ${yearly_budget:,}
    
    The proposal should include:
    1. Executive Summary
    2. Company Background
    3. Proposed Solution (incorporating relevant information from the disaster article)
    4. Timeline
    5. Budget Breakdown
    6. Conclusion
    """
    
    response = client.chat.completions.create(
        model="llama-3.1",
        messages=[
            {"role": "system", "content": "You are a professional proposal writer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )
    
    return response.choices[0].message.content

st.title("Proposal Writer App")

uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
disaster_article = st.text_area("Enter article about the disaster", height=200)
client_logo = st.file_uploader("Upload client logo", type=["png", "jpg", "jpeg"])
yearly_budget = st.number_input("Enter yearly budget", min_value=0, step=1000)

submit_button = st.button("Submit")

if submit_button and uploaded_file and disaster_article and client_logo and yearly_budget:
    document_text = extract_text_from_pdf(uploaded_file)
    extracted_info = extract_info_from_text(document_text)
    
    st.subheader("Extracted Information")
    for info in extracted_info:
        st.write(info)
    
    generate_proposal_button = st.button("Generate Proposal")
    
    if generate_proposal_button:
        with st.spinner("Generating proposal..."):
            proposal = generate_proposal(document_text, disaster_article, yearly_budget, *extracted_info)
        
        st.subheader("Generated Proposal")
        st.write(proposal)
        
        # Display client logo
        st.image(Image.open(client_logo), caption="Client Logo", width=200)
elif submit_button:
    st.warning("Please upload a PDF document, enter the disaster article, upload a client logo, and enter the yearly budget before submitting.")

st.sidebar.write("Proposal Writer App using Llama 3.1 and Groq API")