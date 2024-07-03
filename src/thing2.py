import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import fitz  # PyMuPDF
import os
import logging
from agents import GitHubAgent
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

os.environ["OPENAI_API_KEY"] = "sk-proj-sip24CKwpzxxhR2rKsmgT3BlbkFJVnWUMHc6WOGZdJ4uK8iF"
os.environ["GITHUB_TOKEN"] = "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"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI()

class Message(BaseModel):
    message: str

def get_github_username_from_pdf(name, pdf_path):
    logging.debug(f"Searching for GitHub username in PDF: {pdf_path} with name: {name}")
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text = page.get_text("text")
            lines = text.split('\n')
            for line in lines:
                if name.lower() in line.lower():
                    parts = line.split()
                    for part in parts:
                        if part.startswith("https://github.com/"):
                            username = part.split("/")[-1]
                            logging.debug(f"Found GitHub username: {username}")
                            return username
        logging.debug("GitHub username not found in PDF.")
        return None
    except Exception as e:
        logging.error(f"Error in get_github_username_from_pdf: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-response")
async def generate_response(message: Message):
    try:
        logging.debug(f"Received message: {message.message}")
        response = ""

        if message.message.startswith("https://github.com/"):
            logging.debug("Message is a GitHub URL.")
            git_agent = GitHubAgent(os.environ["GITHUB_TOKEN"])
            repo_contents = git_agent.get_repo_contents(message.message)
            response = "\n".join(repo_contents)
            logging.debug(f"GitHub repo contents response: {response}")

        elif "repos" in message.message.lower():
            logging.debug("Message contains 'repos'.")
            name = message.message.strip().split()[-1]
            github_username = get_github_username_from_pdf(name,
                                                           '/Users/yigitbickici/Documents/GitHub/Unternehmenssoftware-Project/data/belge.pdf')
            logging.debug(f"Extracted GitHub username: {github_username}")

            if github_username:
                git_agent = GitHubAgent(os.environ["GITHUB_TOKEN"])
                repos = git_agent.get_user_repos(github_username)
                response = "\n".join(repos)
                logging.debug(f"GitHub user repos response: {response}")
            else:
                response = "User could not be found."
                logging.debug(f"User not found for name: {name}")

        else:
            logging.debug("Reading PDF content.")
            # Read the PDF content
            doc = fitz.open('/Users/yigitbickici/Documents/GitHub/Unternehmenssoftware-Project/data/belge.pdf')
            text = ""
            for page in doc:
                text += page.get_text()

            # Create an embedding model
            embedding_model = OpenAIEmbeddings()

            # Create a vectorstore using the loaded documents and embedding model
            index_creator = VectorstoreIndexCreator(embedding=embedding_model)
            docs = [text]
            vectorstore = FAISS.from_texts(docs, embedding_model)

            # Create the RetrievalQA chain
            chain = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff",
                                                retriever=vectorstore.as_retriever(), input_key="question")

            # Pass user's message as a query to the chain
            response = chain({"question": message.message})
            response = response['result']  # Assuming 'result' contains the actual response
            logging.debug(f"RetrievalQA response: {response}")

        # Ensure response always has 'response' key
        logging.debug(f"Final response: {response}")
        return {"response": response}

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("thing2:app", host="localhost", port=4000)
