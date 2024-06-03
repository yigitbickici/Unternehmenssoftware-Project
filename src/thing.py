import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
import os
from agents import GitHubAgent
import csv

os.environ["OPENAI_API_KEY"] = "sk-proj-sip24CKwpzxxhR2rKsmgT3BlbkFJVnWUMHc6WOGZdJ4uK8iF"
os.environ["GITHUB_TOKEN"] = "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"

app = FastAPI()

class Message(BaseModel):
    message: str

def get_github_username_from_csv(name):
    with open('/Users/yigitbickici/Documents/GitHub/Unternehmenssoftware-Project/data/database.csv', mode='r') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            if row['Name'].lower() == name.lower():
                return row['Github'].split("/")[-1]
    return None

@app.post("/generate-response")
async def generate_response(message: Message):
    response = ""
    if message.message.startswith("https://github.com/"):
        git_agent = GitHubAgent(os.environ["GITHUB_TOKEN"])
        repo_contents = git_agent.get_repo_contents(message.message)
        response = "\n".join(repo_contents)
    elif "repos" in message.message.lower():
        name = message.message.strip().split()[-1]
        github_username = get_github_username_from_csv(name)
        if github_username:
            git_agent = GitHubAgent(os.environ["GITHUB_TOKEN"])
            repos = git_agent.get_user_repos(github_username)
            response = "\n".join(repos)
        else:
            response = "User could not found."
    else:
        # Load the documents
        loader = CSVLoader(file_path='/Users/yigitbickici/Documents/GitHub/Unternehmenssoftware-Project/data/database.csv')

        # Create an embedding model
        embedding_model = OpenAIEmbeddings()

        # Create an index using the loaded documents and embedding model
        index_creator = VectorstoreIndexCreator(embedding=embedding_model)
        docsearch = index_creator.from_loaders([loader])

        # Create the RetrievalQA chain
        chain = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.vectorstore.as_retriever(), input_key="question")

        # Pass user's message as a query to the chain
        response = chain({"question": message.message})
        response = response['result']

    # Return the response
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("thing:app", host="localhost", port=4000)
