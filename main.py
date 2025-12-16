import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()   # Load environment variables from .env file

st.set_page_config(page_title="AI Resume Critique", page_icon=":📞:", layout="centered")  # Set page title and icon

st.title("AI Resume Critiquer")  # Main title of the app
st.markdown("Upload your resume in PDF format, and receive AI-generated feedback to enhance your resume.")  # Description

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf", "txt"])  # File uploader for PDF resumes
job_role = st.text_input("Enter the job role you are applying for:")  # Input for job role

analyze = st.button("Analyze Resume")  # Button to trigger analysis

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


# Making pdf content bytes to be readable by the PdfReader
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

# If button is clicked
if analyze and uploaded_file is not None:
    try:
        file_content = extract_text_from_file(uploaded_file)  # Extract text from uploaded file
        
        if not file_content.strip():  # Check if the extracted content is empty
            st.error("The uploaded file is empty or could not be read. Please upload a valid PDF or text file.")
            st.stop()
            
        # Create prompt for AI
        prompt = f"""Please analyze this resume and provide consructive feedback.
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}
        
        Resume Content: {file_content}
        
        Please Provide your analysis in a clear, structured format with specific recommendations."""
        
        
        client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                # System message to set the context
                {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."}, 
                
                # User message with the prompt
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,            
        )
        
        st.markdown("### AI Resume Critique:")  # Section title for critique
        st.markdown(response.choices[0].message.content)  # Display AI response
    
    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")  # Display error message
        
    
    

