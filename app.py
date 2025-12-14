import streamlit as st
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate

st.set_page_config(page_title="AskMyPDF", page_icon="📄", layout="centered")
st.title("📄 AskMyPDF")
st.caption("Free · Unlimited · Works on mobile · Dec 2025")

# Simple check for token
if "HF_TOKEN" not in st.secrets:
    st.error("Please add your HF_TOKEN in Secrets (Settings → Secrets) → `HF_TOKEN = hf_yourtokenhere`")
    st.stop()

pdf = st.file_uploader("Upload PDF", type="pdf")
question = st.text_input("Ask anything", placeholder="e.g., What is on page 487?")

@st.cache_resource(show_spinner="Processing PDF...")
def process_pdf(file):
    reader = PdfReader(file)
    text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        text += f"\n\n[Page {i+1}]\n{page_text}"
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
    chunks = splitter.split_text(text)
    return chunks

if pdf and question:
    chunks = process_pdf(pdf)
    
    with st.spinner("Creating vector database (first time only)..."):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_texts(chunks, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

    with st.spinner("Loading Gemma-2-9B and answering..."):
        llm = HuggingFaceEndpoint(
            repo_id="google/gemma-2-9b-it",
            huggingfacehub_api_token=st.secrets["HF_TOKEN"],
            temperature=0.3,
            max_new_tokens=1024
        )

        prompt = PromptTemplate.from_template(
            "Use this context (with page numbers) to answer the question. Always cite pages like [Page 42].\n\n"
            "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

        result = qa.invoke({"query": question})
    
    st.success("Answer:")
    st.markdown(result["result"])
    
    with st.expander(f"Sources ({len(result['source_documents'])} chunks)"):
        for doc in result["source_documents"]:
            st.caption(doc.page_content[:600] + "...")

else:
    st.info("Upload a PDF and ask a question!")

st.markdown("---")
st.markdown("❤️ [Buy me a coffee ☕](https://ko-fi.com/bryantolbert)")
st.caption("Made by never2late4me2 • Working perfectly Dec 07, 2025")
