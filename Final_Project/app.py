"""import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from template import css, bot_template, user_template

def get_cv_content(cv_docs):
    content = ""
    for pdf in cv_docs:
        cv_reader = PdfReader(pdf)
        for page in cv_reader.pages:
            content += page.extract_text()
    return content


def get_content_chunks(raw_content):
    content_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
    chunks = content_splitter.split_text(raw_content)
    return chunks


def get_vstore(chunk_contents):
    embeddings = OpenAIEmbeddings()
    v_store = FAISS.from_texts(texts=chunk_contents, embedding=embeddings)
    return v_store


def get_conversation_chain(v_store):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=v_store.as_retriever(), memory=memory)
    return chain


def handle_input(question):
    ai_response = st.session_state.conversation({'question': question})
    st.session_state.chat_history = ai_response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with CVs")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with CVs")
    question = st.text_input("Ask a question about the personal information from CV:")
    if question:
        handle_input(question)

    with st.sidebar:
        st.subheader("Your CVs")
        pdf_docs = st.file_uploader("Upload your CV here and click on 'Run the CV(s)'", accept_multiple_files=True)
        if st.button("Run the CV(s)"):
            with st.spinner("In progress"):
                # get pdf text
                raw_content = get_cv_content(pdf_docs)

                # get the text chunks
                content_chunks = get_content_chunks(raw_content)

                # create vector store
                v_store = get_vstore(content_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(v_store)


if __name__ == '__main__':
    main()
"""

import streamlit as st
from dotenv import load_dotenv
import pickle
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import os

# Sidebar contents
with st.sidebar:
    st.title('🤗💬 LLM Chat App')
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit](https://streamlit.io/)
    - [LangChain](https://python.langchain.com/)
    - [OpenAI](https://platform.openai.com/docs/models) LLM model
    ''')

load_dotenv()

def main():
    st.header("Chat with PDF 💬")

    # Sistem promptu
    system_prompt = (
        "You are a head hunter assistant who can answer questions based on the content of a CV file."
        "Your task is giving information about the person I provide you, and help me to whether I hire the person or not."
        "You should provide clear and concise answers, and if the information is not present in the PDF, "
        "please indicate that the information is not available."
    )

    # upload a PDF file
    pdf = st.file_uploader("Upload your PDF", type='pdf')

    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text=text)

        store_name = pdf.name[:-4]
        st.write(f'{store_name}')

        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
                VectorStore = pickle.load(f)
        else:
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            with open(f"{store_name}.pkl", "wb") as f:
                pickle.dump(VectorStore, f)

        query = st.text_input("Ask questions about your PDF file:")

        if query:
            docs = VectorStore.similarity_search(query=query, k=3)

            llm = OpenAI()
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=query, system_prompt=system_prompt)
                print(cb)
            st.write(response)

if __name__ == '__main__':
    main()