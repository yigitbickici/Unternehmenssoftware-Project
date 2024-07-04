import streamlit as st 
from backend import comp_process
from dotenv import load_dotenv

load_dotenv()

api_key= "sk-proj-sip24CKwpzxxhR2rKsmgT3BlbkFJVnWUMHc6WOGZdJ4uK8iF"

def frontend():
# Streamlit UI
    st.set_page_config(page_title="Chat with multiple pdf files")
    st.title("Chat with Multiple : red [PDF Files]!")
    question = st.text_input("Ask Question Below: ")
    
    with st.sidebar:
        st. subheader("Upload PDFs here")
        pdfs = st.file_uploader ("Upload PDF files" , type="pdf", accept_multiple_files=True)
        st.button ('Process')

    if pdfs and api_key is not None:
        if question:
            ans = comp_process(apikey=api_key, pdfs=pdfs, question=question)
            st.text(ans)

if __name__=="__main__":
    frontend()