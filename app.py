import streamlit as st
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.retrieval_qa.base import RetrievalQA # FIX APPLIED HERE
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import os

# ========================= CONFIG & CONSTANTS =========================
st.set_page_config(page_title="AskMyPDFs Pro", page_icon="📚", layout="wide")

# Initialize Text Splitter once for performance
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=400,
    separators=["\n\n", "\n", " ", ""],
    keep_separator=True
)

# ========================= UI COMPONENTS =========================

def render_sidebar():
    """Renders the application sidebar with instructions and tech stack."""
    with st.sidebar:
        st.title("📚 AskMyPDFs Pro")
        st.caption("Multi‑PDF Question Answering with Advanced RAG")
        
        st.markdown("---")
        st.markdown("### 💡 How to Use")
        st.markdown("""
        1. **Upload** one or more PDFs in the main area.
        2. **Wait** for the vector database to build (cached for speed).
        3. **Ask** any question about the documents.
        4. **Filter** the search to a specific document if needed.
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Tech Stack")
        st.markdown("""
        - **LLM:** Gemma-2-9B (via HuggingFace)
        - **Embeddings:** MiniLM-L6-v2 (Optimized)
        - **Vector DB:** FAISS
        - **Framework:** LangChain & Streamlit
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

def render_footer():
    """Renders the application footer."""
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:#888;'>"
        "Made with ❤️ by Bryant Olbert • Refactored by Manus AI"
        "</p>",
        unsafe_allow_html=True
    )

# ========================= HELPERS (LOGIC) =========================

@st.cache_resource(show_spinner="Extracting text from PDFs...")
def process_pdfs(uploaded_files):
    """Extract text from PDFs with page-level tracking and chunking."""
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
                        # Use the pre-initialized global splitter
                        chunks = TEXT_SPLITTER.split_text(page_text)
                        for chunk in chunks:
                            # Robustness: Filter out empty chunks
                            if chunk.strip():
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
    """Create FAISS vector store from Document objects."""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            # Performance: Removed model_kwargs={'device': 'cpu'} to allow GPU usage if available
            encode_kwargs={'normalize_embeddings': True}
        )
        vectorstore = FAISS.from_documents(docs, embeddings)
        return vectorstore
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        raise

def get_hf_token():
    """Standardize HuggingFace token retrieval."""
    # Maintainability: Use st.secrets.get() which also checks environment variables
    hf_token = st.secrets.get("HF_TOKEN") or os.environ.get("HF_TOKEN")
    
    if not hf_token:
        st.error("HuggingFace token not found. Please add HF_TOKEN to your Streamlit secrets or environment.")
        st.stop()
    return hf_token

def build_qa_chain(vectorstore, filter_doc=None):
    """Build QA chain with LLM and retriever using metadata filtering."""
    try:
        hf_token = get_hf_token()
        
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

        # Robustness: Increased k to 50 for a larger pool for post-retrieval filtering
        base_retriever = vectorstore.as_retriever(search_kwargs={"k": 50})

        if filter_doc and filter_doc != "All PDFs":
            # Custom filtering function for document-specific search
            def filtered_get_relevant_documents(query):
                docs = base_retriever.get_relevant_documents(query)
                # Filter the large pool of retrieved documents
                filtered = [doc for doc in docs if doc.metadata.get("source") == filter_doc]
                # Return a reasonable number of top-ranked, filtered documents
                return filtered[:6]
            
            # Monkey-patch the retriever method with the filtered version
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

# ========================= MAIN APPLICATION FLOW =========================

def render_main_app():
    """Renders the main content and handles the application logic."""
    st.title("Ask Questions Across Your PDFs")
    st.caption("Upload multiple PDFs and get AI-powered answers with source citations")

    # --- File Uploader and Question Input ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
        pdfs = st.file_uploader(
            "Upload one or more PDFs", 
            type="pdf", 
            accept_multiple_files=True,
            key="pdf_uploader"
        )
        
    with col2:
        question = st.text_input(
            "Ask anything across your PDFs",
            placeholder="e.g., Compare introductions • Summarize references • What is said on page 42 of doc2?",
            key="question_input"
        )

    # --- Core Logic ---
    if pdfs:
        # Process PDFs and create vector store (cached)
        docs, doc_index = process_pdfs(pdfs)
        
        if not docs:
            st.error("No text could be extracted from the uploaded PDFs. Please check your files.")
            return

        # Store state in session_state
        st.session_state["docs"] = docs
        st.session_state["doc_index"] = doc_index
        
        # Display document summary
        with st.expander("Uploaded Document Summary", expanded=False):
            st.markdown("##### Extracted Chunks:")
            for name, pages, chunks_count in doc_index:
                st.markdown(f"- **{name}**: {pages} pages → {chunks_count} chunks")

        # Create vector store (cached)
        vectorstore = create_vectorstore(docs)
        st.session_state["vectorstore"] = vectorstore
        
        # Document Filter and QA Chain Setup
        doc_names = ["All PDFs"] + [name for name, _, _ in doc_index]
        filter_choice = st.selectbox(
            "Restrict search to:", 
            doc_names, 
            key="doc_filter",
            help="Select a specific PDF to narrow the search context, or use 'All PDFs' for a comprehensive search."
        )
        
        # Build QA Chain (not cached, as filter_choice changes the retriever)
        qa_chain = build_qa_chain(vectorstore, filter_choice)
        st.session_state["qa_chain"] = qa_chain

        # --- Question Answering Execution ---
        if question:
            try:
                with st.spinner("🤔 Querying the model..."):
                    result = qa_chain.invoke({"query": question})

                answer = result["result"]
                sources = result["source_documents"]

                # --- Results Display ---
                st.markdown("---")
                st.subheader("✅ AI Answer")
                st.info(answer) # Use st.info for a prominent answer box

                if sources:
                    with st.expander(f"📄 Sources Used ({len(sources)} chunks)", expanded=True):
                        for i, doc in enumerate(sources, 1):
                            preview = doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else "")
                            st.markdown(f"**Source {i}:** `{doc.metadata['source']}` – Page **{doc.metadata['page']}**")
                            st.code(preview, language="text")
                            st.divider()
                
            except Exception as e:
                st.error(f"An error occurred during the QA process: {str(e)}")
                st.info("Please ensure your HuggingFace token is correctly configured and try again.")

        else:
            st.success("✅ PDFs loaded and vector database ready! Now type your question above.")
            
    else:
        st.info("👆 Upload one or more PDFs to begin your AI-powered document analysis.")


# ========================= ENTRY POINT =========================
if __name__ == "__main__":
    render_sidebar()
    render_main_app()
    render_footer()
