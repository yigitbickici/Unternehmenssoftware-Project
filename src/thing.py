import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
import os

os.environ["OPENAI_API_KEY"] = "sk-proj-sip24CKwpzxxhR2rKsmgT3BlbkFJVnWUMHc6WOGZdJ4uK8iF"

app = FastAPI()

class Message(BaseModel):
    message: str

@app.post("/generate-response")
async def generate_response(message: Message):
    # Load the documents
    loader = CSVLoader(file_path='/Users/yigitbickici/Documents/GitHub/Unternehmenssoftware-Project/data/database.csvs')

    # Create an embedding model
    embedding_model = OpenAIEmbeddings()

    # Create an index using the loaded documents and embedding model
    index_creator = VectorstoreIndexCreator(embedding=embedding_model)
    docsearch = index_creator.from_loaders([loader])

    # Create the RetrievalQA chain
    chain = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.vectorstore.as_retriever(), input_key="question")

    # Pass user's message as a query to the chain
    response = chain({"question": message.message})
    
    # Return the response
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("thing:app", host="localhost", port=4000)
