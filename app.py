from dotenv import load_dotenv
import os
import io
import base64
import fitz  # PyMuPDF
import streamlit as st
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def convert_pdf_to_images(file_bytes):
    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
    images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img_byte_arr = io.BytesIO(pix.tobytes())
        images.append(Image.open(img_byte_arr))
    return images

def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model
    response = model.generate_content([input_text, pdf_content[0], prompt])
    # Check the structure of the response and adjust accordingly
    if hasattr(response, 'text'):
        return response.text
    elif hasattr(response, 'content'):
        return response.content
    else:
        return "Response content is not available"

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = convert_pdf_to_images(uploaded_file.read())

        first_page = images[0]

        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]

        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

st.set_page_config(page_title="ATS Resume Expert", layout="wide")
st.header("ATS Tracking System")

input_text = st.text_area("Job Description:", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell me about the Resume")
submit2 = st.button("How can I improve my skills")
submit3 = st.button("Percentage match")

input_prompt1 = """
You are an experienced HR professional with expertise in the following job roles: data science, full-stack web development, big data engineering, DevOps, data analyst, and AI. Your task is to review the provided resume against the job description for these profiles. Please provide a professional evaluation of whether the candidate's profile aligns with the role. Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
You are a technical HR manager with expertise in the following fields: data science, full-stack web development, big data engineering, DevOps, data analyst, and AI. Your role is to scrutinize the resume in light of the provided job description. Please provide a professional evaluation of whether the candidate's profile aligns with the role. Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an ATS (Applicant Tracking System) scanner with a deep understanding of the following job roles: data science, full-stack web development, big data engineering, DevOps, data analyst, and AI, as well as deep ATS functionality. Your task is to evaluate the resume against the provided job description. Provide the percentage match if the resume aligns with the job description. First, output the percentage, then keywords missing, and finally, your thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        responses = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("The response is")
        st.write(responses)
    else:
        st.write("Please upload a PDF")

elif submit2:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        responses = get_gemini_response(input_text, pdf_content, input_prompt2)
        st.subheader("The response is")
        st.write(responses)
    else:
        st.write("Please upload a PDF")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        responses = get_gemini_response(input_text, pdf_content, input_prompt3)
        st.subheader("The response is")
        st.write(responses)
    else:
        st.write("Please upload a PDF")
