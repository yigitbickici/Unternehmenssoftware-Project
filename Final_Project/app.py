import streamlit as st
from dotenv import load_dotenv
import os
import pickle
import re
from github import Github
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback


class GitHubAgent:
    def __init__(self, token):
        self.g = Github(token)

    def get_user_repos(self, username):
        try:
            user = self.g.get_user(username)
            repos = user.get_repos()
            return [repo.name for repo in repos]
        except Exception as e:
            return str(e)

    def _extract_repo_name(self, repo_url):
        match = re.match(r'https://github.com/([^/]+/[^/]+)', repo_url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid GitHub repository URL")

    def _get_all_contents(self, repo, contents, all_files=[]):
        for content_file in contents:
            if content_file.type == "dir":
                all_files = self._get_all_contents(repo, repo.get_contents(content_file.path), all_files)
            else:
                all_files.append(content_file.path)
        return all_files


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


def extract_github_username(text):
    # Basic regex to extract GitHub usernames or URLs
    github_url_pattern = r"https://github\.com/([a-zA-Z0-9-]+)"
    github_username_pattern = r"\bgithub\.com/([a-zA-Z0-9-]+)\b"

    urls = re.findall(github_url_pattern, text)
    usernames = re.findall(github_username_pattern, text)

    return urls + usernames


def main():
    st.header("Chat with PDF 💬")

    # Sistem promptu
    system_prompt = (
        "You are a head hunter assistant who can answer questions based on the content of a CV file."
        "You need to analyze informations from CV file and can make comments about the owner of the CV"
        "Your task is giving information about the the owners of the CV files I will provide you, and help me to whether I hire the person or not."
        "You should provide clear and concise answers because people who are hiring will ask you questions"
    )

    # GitHub Token from environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    github_agent = GitHubAgent(github_token)

    # Upload PDF files
    pdf_files = st.file_uploader("Upload your PDF(s)", type='pdf', accept_multiple_files=True)

    if pdf_files:
        vector_stores = {}

        for pdf_file in pdf_files:
            pdf_reader = PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            github_usernames = extract_github_username(text)
            if github_usernames:
                st.write(f"Found GitHub profiles: {github_usernames}")

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(text=text)

            store_name = pdf_file.name[:-4]
            st.write(f'{store_name}')

            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            vector_stores[store_name] = VectorStore

            # Save the FAISS index
            with open(f"{store_name}_index.pkl", "wb") as f:
                pickle.dump(VectorStore.index, f)
            with open(f"{store_name}_texts.pkl", "wb") as f:
                pickle.dump(chunks, f)

        query = st.text_input("Ask questions about your PDF file:")

        if query:
            responses = []
            for store_name, VectorStore in vector_stores.items():
                docs = VectorStore.similarity_search(query=query, k=5)

                llm = OpenAI()
                chain = load_qa_chain(llm=llm, chain_type="stuff")
                with get_openai_callback() as cb:
                    response = chain.run(input_documents=docs, question=query, system_prompt=system_prompt)
                    responses.append(response)
                    print(cb)

            for response in responses:
                st.write(response)

            if "github" in query.lower():
                for username in github_usernames:
                    repos = github_agent.get_user_repos(username)
                    st.write(f"GitHub Repositories for {username}: {repos}")


if __name__ == '__main__':
    main()
