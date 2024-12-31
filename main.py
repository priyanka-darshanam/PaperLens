import os
import streamlit as st
import pickle
from langchain_community.llms import OpenAI
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.schema import Document


from dotenv import load_dotenv

load_dotenv()

st.title("PaperLens")

st.sidebar.title("Research URLs")

urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

process_url_clicked = st.sidebar.button("Process URLs")
file_path = "faiss_store_openai.pkl"

main_placeholder = st.empty()
llm = OpenAI(temperature=0.9, max_tokens=500)

if process_url_clicked:
    loader = UnstructuredURLLoader(urls=urls)
    main_placeholder.text("Loading...")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],
        chunk_size=1000
    )
    main_placeholder.text("Text splitting...")

    docs = text_splitter.split_documents(data)

    embeddings = OpenAIEmbeddings()
    vectorstore_openai = FAISS.from_documents(docs, embeddings)
    main_placeholder.text("Embedding Vector Started Building...")

    texts = [doc.page_content for doc in docs]
    with open(file_path, "wb") as f:
        pickle.dump(texts, f)

    vectorstore_openai.save_local("faiss_index")

query = st.text_input("Quest: ")
if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            texts = pickle.load(f)

            docs = [Document(page_content=text) for text in texts]

            vectorstore_openai = FAISS.load_local("faiss_index", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
            retriever = vectorstore_openai.as_retriever()

            chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=retriever)
            result = chain({"question": query}, return_only_outputs=True)

            st.header("Result")
            st.write(result["answer"])
