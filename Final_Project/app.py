import streamlit as st
from dotenv import load_dotenv
import os
import pickle
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# Load environment variables
load_dotenv()

def extract_github_username(text):
    github_url_pattern = r"https://github\.com/([a-zA-Z0-9-]+)"
    github_username_pattern = r"\bgithub\.com/([a-zA-Z0-9-]+)\b"

    urls = re.findall(github_url_pattern, text)
    usernames = re.findall(github_username_pattern, text)

    return urls + usernames

def extract_emails(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails

def mail_send(receiver_email, subject, message):
    sender_email = "deyapp.serefini@gmail.com"
    password = "idjkrnlpsgvifppz"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        st.success("E-mail sent successfully.")
    except Exception as e:
        st.error(f"E-mail isn't sent. Error: {e}")
    finally:
        server.quit()

def pdf_extractor(pdf_files):

    if pdf_files:
        combined_text = ""
        github_usernames = set()
        emails = set()

        for pdf_file in pdf_files:
            pdf_reader = PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            usernames = extract_github_username(text)
            github_usernames.update(usernames)

            extracted_emails = extract_emails(text)
            emails.update(extracted_emails)

            combined_text += text + "\n\n"

        if github_usernames:
            st.write(f"Found GitHub profiles: {list(github_usernames)}")

        if emails:
            st.write(f"Found email addresses: {list(emails)}")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text=combined_text)

        embeddings = OpenAIEmbeddings()
        VectorStore = FAISS.from_texts(chunks, embedding=embeddings)

        st.session_state.VectorStore = VectorStore
        st.session_state.emails = emails

        with open("combined_index.pkl", "wb") as f:
            pickle.dump(VectorStore.index, f)
        with open("combined_texts.pkl", "wb") as f:
            pickle.dump(chunks, f)

def comparing_and_analyzing_cvs(default_system_prompt,github_agent):
    st.header("Comparing and Analyzing CV(s)")

    options = ["Education", "Skills", "Projects", "Experiences"]
    st.text("QUICK ACCESS")
    selected_options = st.multiselect("Select the features you want to compare:", options)

    custom_prompt = st.text_area("Enter your custom prompt (optional):")

    context = []

    if st.button("Process"):
        if not selected_options and not custom_prompt:
            st.write("Please select features or enter a custom prompt.")
        else:
            query = ""
            if selected_options:
                query += "Compare the CVs based on the following features and use the candidates names in the CVs while generating the response: " + ", ".join(
                    selected_options) + "."
            if custom_prompt:
                query += " " + custom_prompt

            docs = st.session_state.VectorStore.similarity_search(query=query, k=10)

            llm = OpenAI()
            chain = load_qa_chain(llm=llm, chain_type="stuff")

            final_prompt = (custom_prompt if custom_prompt else default_system_prompt) + "\n\n" + "\n\n".join(context)

            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=query, system_prompt=final_prompt)
                st.write('<div class="bot_template">', unsafe_allow_html=True)

            context.append(f"Question: {query}\nAnswer: {response}")

            if "github" in query.lower():
                for username in st.session_state.github_usernames:
                    repos = github_agent.get_user_repos(username)
                    st.write(f"GitHub Repositories for {username}: {repos}")

def send_email_to_candidates():
    st.header("Send E-mail to Candidates")

    if 'VectorStore' not in st.session_state or 'emails' not in st.session_state:
        st.error("No data available. Please upload and process CVs first.")
        return

    emails = st.session_state.emails
    VectorStore = st.session_state.VectorStore

    if emails:
        receiver_email = st.selectbox("Select email to send:", list(emails))
        subject = st.text_input("Subject")
        email_prompt = st.text_area("What would you like to include in the email? Describe the content.")

        if st.button("Send Email"):
            if receiver_email and subject and email_prompt:
                email_query = f"Write an email with the following content: {email_prompt}"
                docs = VectorStore.similarity_search(query=email_query, k=5)

                llm = OpenAI()
                chain = load_qa_chain(llm=llm, chain_type="stuff")

                with get_openai_callback() as cb:
                    email_message = chain.run(input_documents=docs, question=email_query, system_prompt=default_system_prompt)

                mail_send(receiver_email, subject, email_message)
            else:
                st.error("Please fill in all fields to send an email.")

def main():
    default_system_prompt = (
        "You are a headhunter assistant in DEYapp Software Company who can answer questions based on the content of CV files."
        "You need to analyze information from the CV files and make comments about the owners of the CVs. "
        "Your task is to provide information about the owners of the CV files I provide you, and help me decide whether to hire the person or not. "
        "You should provide clear and concise answers because people who are hiring will ask you questions."
    )

    github_token = os.getenv('GITHUB_TOKEN')
    github_agent = GitHubAgent(github_token)

    st.title("WELCOME TO HEAD HUNTER CV CHATBOT")
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    pdf_files = st.file_uploader("Upload your PDF(s)", type='pdf', accept_multiple_files=True)
    pdf_extractor(pdf_files)

    if st.button("Comparing and Analyzing CV(s)"):
        st.session_state.page = 'compare_analyze'
        st.experimental_rerun()

    if st.button("Send E-mail to candidates"):
        st.session_state.page = 'send_email'
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if 'page' in st.session_state:
        if st.session_state.page == 'compare_analyze':
            comparing_and_analyzing_cvs(default_system_prompt,github_agent)
        elif st.session_state.page == 'send_email':
            send_email_to_candidates()

if __name__ == '__main__':
    main()
