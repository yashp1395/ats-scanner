import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import time

load_dotenv() ## load all our environment variables

# Use the environment variable for the API key if available
# Note: In the final deployment environment, the key will be handled automatically.
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
# else:
#     st.error("GOOGLE_API_KEY environment variable not set. Please set it up.")


def get_gemini_repsonse(input_prompt_text):
    """
    Calls the Gemini Pro model with the fully constructed text prompt.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        # Use a timeout or retry logic for robustness in a real app
        response = model.generate_content(input_prompt_text)
        return response.text
    except Exception as e:
        # Handle API errors gracefully
        st.error(f"Error during API call: {e}")
        return None

def input_pdf_text(uploaded_file):
    """
    Extracts text content from an uploaded PDF file.
    """
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())
    return text

# Prompt Template: Ensures the response is structured as JSON
input_prompt="""
Hey Act Like a skilled or very experience ATS (Application Tracking System) 
with a deep understanding of tech field, software engineering, data science, data analyst,
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on Jd and the missing keywords with high accuracy.

The resume content is provided in `resume` and the job description in `description`.

resume:
{text}

description:
{jd}

I want the response as a single, valid JSON object, and ONLY the JSON object, 
matching the following structure exactly:
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""

## streamlit app

st.set_page_config(page_title="Smart ATS for Resumes", layout="wide")

with st.sidebar:
    st.title("Smart ATS for Resumes")
    st.subheader("About")
    st.write("This sophisticated ATS project, developed with **Gemini Pro** and **Streamlit**, streamlines hiring by analyzing resumes against job descriptions, providing match percentage, missing keywords, and profile summaries.")
    
    st.markdown("""
    - [Streamlit](https://streamlit.io/)
    - [Gemini Pro](https://deepmind.google/technologies/gemini/#introduction)
    - [Github Repository](https://github.com/praj2408/End-To-End-Resume-ATS-Tracking-LLM-Project-With-Google-Gemini-Pro)
                
    """)
    
    add_vertical_space(5)
    st.write("Made with ❤️ by Prajwal Krishna.")
    


st.title("Smart Application Tracking System")
st.text("Improve Your Resume ATS Score")
jd=st.text_area("1. Paste the Job Description here (Required)", height=200)
uploaded_file=st.file_uploader("2. Upload Your Resume (PDF Required)", type="pdf", help="Please upload a PDF resume file.")

submit = st.button("3. Analyze Resume")

if submit:
    if not jd:
        st.warning("Please paste the Job Description before submitting.")
    elif uploaded_file is None:
        st.warning("Please upload your resume (PDF) before submitting.")
    else:
        # 1. Extract text from PDF
        with st.spinner('Extracting text from resume...'):
            resume_text = input_pdf_text(uploaded_file)

        # 2. Format the prompt with actual data (The CRITICAL FIX)
        final_prompt = input_prompt.format(text=resume_text, jd=jd)
        
        # 3. Call the Gemini API
        with st.spinner('Analyzing resume with Gemini Pro...'):
            response_text = get_gemini_repsonse(final_prompt)
        
        if response_text:
            st.subheader("ATS Analysis Results")
            st.markdown("---")
            
            try:
                # Attempt to parse the structured JSON response
                data = json.loads(response_text)
                
                # Display JD Match
                match_percent = data.get('JD Match', 'N/A')
                st.markdown(f"**Job Description Match:**")
                st.progress(int(match_percent.replace('%', '')) / 100)
                st.markdown(f"## {match_percent}")
                
                st.markdown("---")
                
                # Display Missing Keywords
                st.markdown("**Missing Keywords for Improvement:**")
                missing_keywords = data.get('MissingKeywords', [])
                if missing_keywords and isinstance(missing_keywords, list):
                    for keyword in missing_keywords:
                        st.markdown(f"- {keyword}")
                else:
                    st.success("Great job! Your resume appears to cover all the key skills.")
                    
                st.markdown("---")
                
                # Display Profile Summary
                st.subheader("Detailed Profile Summary & Suggestions")
                st.write(data.get('Profile Summary', 'The model did not provide a summary.'))
                
            except json.JSONDecodeError:
                st.error("The model returned a response but it was not a valid JSON structure. Displaying raw output for debugging:")
                st.code(response_text)
            except Exception as e:
                st.error(f"An unexpected error occurred during result display: {e}")
