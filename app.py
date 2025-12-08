import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain.schema import Document
import os

# ========================= CONFIG =========================
st.set_page_config(page_title="AskMyPDFs", page_icon="📚", layout="centered")

# ========================= SIDEBAR =========================
with st.sidebar:
    st.title("📚 AskMyPDFs")
    st.caption("Multi‑PDF Question Answering")
    
    st.markdown("---")
    st.markdown("### 💡 How to Use")
    st.markdown("""
    1. Upload one or more PDFs
    2. Ask any question about them
    3. Get answers with citations
    4. Filter by specific documents
    """)
    
    st.markdown("---")
    st.markdown("### ☕ Support This Project")
    st.markdown(
        """
        <div style='text-align:center; margin: 20px 0;'>
            <a href='https://ko-fi.com/bryantolbert' target='_blank'>
                <img height='36' style='border:0px;height:36px;' 
                     src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' 
                     border='0' alt='Buy Me a Coffee at ko-fi.com' />
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.markdown("### 🔧 Tech Stack")
    st.markdown("""
    - **LLM:** Gemma-2-9B
    - **Embeddings:** MiniLM-L6-v2
    - **Vector DB:** FAISS
    - **Framework:** LangChain
    """)

# ========================= MAIN CONTENT =========================
st.title("📚 Ask Questions Across Your PDFs")
st.caption("Upload multiple PDFs and get AI-powered answers with source citations")

# ========================= INPUTS =========================
pdfs = st.file_uploader("Upload one or more PDFs", type="pdf", accept_multiple_files=True)
question = st.text_input(
    "Ask anything across your PDFs",
    placeholder="e.g., Compare introductions • Summarize references • What is said on page 42 of doc2?"
)

# ========================= HELPERS =========================
@st.cache_resource(show_spinner="Extracting text from PDFs...")
def process_pdfs(uploaded_files):
    """Extract text from PDFs with page-level tracking"""
    all_docs = []
    doc_index = []
    
    for uploaded_file in uploaded_files:
        try:
            reader = PdfReader(uploaded_file)
            doc_chunks = []
            
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=2000,
                            chunk_overlap=400,
                            separators=["\n\n", "\n", " ", ""],
                            keep_separator=True
                        )
                        chunks = splitter.split_text(page_text)
                        for chunk in chunks:
                            doc = Document(
                                page_content=chunk,
                                metadata={"source": uploaded_file.name, "page": i+1}
                            )
                            all_docs.append(doc)
                            doc_chunks.append(doc)
                except Exception as e:
                    st.warning(f"Could not extract page {i+1} from {uploaded_file.name}: {str(e)}")
                    continue
            
            doc_index.append((uploaded_file.name, len(reader.pages), len(doc_chunks)))
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            continue
    
    return all_docs, doc_index

@st.cache_resource(show_spinner="Building vector database...")
def create_vectorstore(docs):
    """Create FAISS vector store from Document objects"""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        vectorstore = FAISS.from_documents(docs, embeddings)
        return vectorstore
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        raise

def build_qa_chain(vectorstore, filter_doc=None):
    """Build QA chain with LLM and retriever using metadata filtering"""
    try:
        hf_token = st.secrets["HF_TOKEN"] if "HF_TOKEN" in st.secrets else os.environ.get("HF_TOKEN")
        
        if not hf_token:
            st.error("HuggingFace token not found. Please add HF_TOKEN to your secrets or environment.")
            st.stop()
        
        llm = HuggingFaceEndpoint(
            repo_id="google/gemma-2-9b-it",
            huggingfacehub_api_token=hf_token,
            temperature=0.3,
            max_new_tokens=1024,
        )

        prompt_template = """You are an expert assistant analyzing multiple PDFs.
Use the following context (with file names and page numbers) to answer concisely.

Context:
{context}

Question: {question}

Instructions:
- Always cite both file name and page numbers, e.g. [doc1.pdf – Page 42].
- If not found, say "Not found in the documents."
- Keep the answer clear and professional.

Answer:"""

        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        base_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

        if filter_doc and filter_doc != "All PDFs":
            def filtered_get_relevant_documents(query):
                docs = base_retriever.get_relevant_documents(query)
                filtered = [doc for doc in docs if doc.metadata.get("source") == filter_doc]
                return filtered[:6]
            
            base_retriever.get_relevant_documents = filtered_get_relevant_documents

        retriever = base_retriever

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        return qa_chain
        
    except Exception as e:
        st.error(f"Error building QA chain: {str(e)}")
        raise

# ========================= MAIN EXECUTION =========================
if pdfs and question:
    try:
        with st.status("Processing PDFs...", expanded=False) as status:
            docs, doc_index = process_pdfs(pdfs)
            
            if not docs:
                st.error("No text could be extracted from the uploaded PDFs. Please check your files.")
                st.stop()
            
            st.write("Extracted chunks:")
            for name, pages, chunks_count in doc_index:
                st.write(f"- {name}: {pages} pages → {chunks_count} chunks")

            vectorstore = create_vectorstore(docs)
            st.write("✅ Vector database ready")

            doc_names = ["All PDFs"] + [name for name, _, _ in doc_index]
            filter_choice = st.selectbox("Restrict search to:", doc_names, key="doc_filter")

            qa_chain = build_qa_chain(vectorstore, filter_choice)
            
            st.write("🤔 Querying the model...")
            result = qa_chain.invoke({"query": question})

            answer = result["result"]
            sources = result["source_documents"]

            status.update(label="✅ Done!", state="complete", expanded=False)

        st.success("Answer")
        st.markdown(answer)

        if sources:
            with st.expander(f"📄 Show sources ({len(sources)} chunks used)"):
                for i, doc in enumerate(sources, 1):
                    preview = doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else "")
                    st.caption(f"**Source {i}: {doc.metadata['source']} – Page {doc.metadata['page']}**")
                    st.text(preview)
                    st.divider()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try again or check your HuggingFace token configuration.")

elif pdfs and not question:
    st.info("✅ PDFs loaded! Now type your question above.")
else:
    st.info("👆 Upload one or more PDFs and ask your question!")

# ========================= FOOTER =========================
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#888;'>"
    "Made with ❤️ by Bryant Olbert • Updated Dec 08, 2025"
    "</p>",
    unsafe_allow_html=True
)
