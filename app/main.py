import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST before importing anything else
# Explicitly point to the .env file in the parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import PyPDF2
import io

from chains import Chain
from utils import clean_text


def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF resume"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def create_streamlit_app(llm, clean_text):
    st.title("📧 Personalized Cold Email Generator")
    
    st.markdown("""
    Generate tailored cold emails by uploading your resume and providing a job posting link.
    """)
    
    # Two columns for better layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Your Information")
        
        # Option to input text or upload resume
        input_method = st.radio("Choose input method:", ["Text Input", "Upload Resume (PDF)"])
        
        if input_method == "Text Input":
            user_name = st.text_input("Your Name:", value="Aditya Agrahari")
            user_info = st.text_area(
                "About You (Skills, Experience, Projects):",
                height=200,
                placeholder="Enter your skills, experience, projects, and what makes you unique..."
            )
        else:
            user_name = st.text_input("Your Name:", value="Aditya Agrahari")
            uploaded_file = st.file_uploader("Upload your resume (PDF)", type=['pdf'])
            user_info = None
            
            if uploaded_file is not None:
                with st.spinner("Extracting information from resume..."):
                    user_info = extract_text_from_pdf(uploaded_file)
                    st.success("✅ Resume uploaded successfully!")
    
    with col2:
        st.subheader("💼 Job Posting")
        url_input = st.text_input("Job Posting URL:", value="https://jobs.nike.com/job/R-33460")
    
    submit_button = st.button("🚀 Generate Cold Email", type="primary")

    if submit_button:
        if not user_info:
            st.error("⚠️ Please provide your information (either text or upload a resume)")
            return
            
        try:
            with st.spinner("Fetching job details..."):
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)
                jobs = llm.extract_jobs(data)
            
            with st.spinner("Generating personalized cold email..."):
                for idx, job in enumerate(jobs):
                    email = llm.write_mail(job, user_info, user_name)
                    
                    st.success("✅ Cold email generated!")
                    st.markdown("---")
                    st.subheader(f"📧 Your Personalized Cold Email for: {job.get('role', 'Position')}")
                    
                    # Display email in a container with proper formatting
                    with st.container():
                        st.markdown(email)
                    
                    st.markdown("")  # Add spacing
                    
                    # Copy button with unique key
                    st.download_button(
                        label="📋 Download Email",
                        data=email,
                        file_name=f"cold_email_{job.get('role', 'job').replace(' ', '_')}.txt",
                        mime="text/plain",
                        key=f"download_btn_{idx}"
                    )
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, clean_text)


