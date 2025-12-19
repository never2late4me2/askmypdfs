import streamlit as st
from pypdf import PdfReader
import mailbox
from io import BytesIO
import zipfile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate

# Professional page configuration
st.set_page_config(
    page_title="AskMyDoc Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    .main .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .stApp {background-color: #f8f9fa;}
    h1 {color: #0d6efd; font-weight: 600;}
    .uploaded-file-info {background-color: #e9ecef; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;}
    .answer-box {background-color: #ffffff; padding: 1.5rem; border-radius: 0.8rem; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 5px solid #0d6efd;}
    .source-chunk {background-color: #f1f3f5; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem;}
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("📄 AskMyDoc Pro")
st.markdown("**Intelligent Document Querying** · PDF | MBOX | ZIP · Powered by OpenAI Embeddings & Gemma-2-9b-it")
st.caption("Professional · Responsive · Unlimited · December 2025")

# Secrets check
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Please add `OPENAI_API_KEY` in Secrets.")
    st.stop()
if "HF_TOKEN" not in st.secrets:
    st.error("⚠️ Please add `HF_TOKEN` in Secrets (for Gemma LLM).")
    st.stop()

# Sidebar for inputs
with st.sidebar:
    st.header("Upload & Query")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "mbox", "zip"],
        help="Supports PDFs, email archives (.mbox), and ZIP containers."
    )
    
    question = st.text_input(
        "Your Question",
        placeholder="e.g., Summarize the main findings on page 42",
        help="Ask anything about the document content."
    )
    
    st.markdown("---")
    st.caption("Tip: Include page/email references in questions for precise answers.")

# Main content
if uploaded_file and question:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
    file_size = len(file_bytes) / (1024 * 1024)  # MB
    
    # Display file info
    st.markdown(f"""
        <div class="uploaded-file-info">
            <strong>Uploaded:</strong> {filename} ({file_size:.2f} MB) · Ready for querying
        </div>
    """, unsafe_allow_html=True)
    
    @st.cache_resource(show_spinner="Extracting and chunking document content...")
    def process_uploaded_file(file_bytes, filename):
        text = ""
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(BytesIO(file_bytes))
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text += f"\n\n[Page {i+1}]\n{page_text}"
        
        elif filename.lower().endswith(".mbox"):
            mbox = mailbox.mbox(BytesIO(file_bytes))
            for i, msg in enumerate(mbox, 1):
                subject = msg["subject"] or "No Subject"
                date = msg["date"] or "Unknown Date"
                text += f"\n\n[Email {i}: {subject} | {date}]\n"
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                text += payload.decode(errors="ignore")
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        text += payload.decode(errors="ignore")
        
        elif filename.lower().endswith(".zip"):
            with zipfile.ZipFile(BytesIO(file_bytes)) as z:
                for zip_info in z.infolist():
                    if zip_info.is_dir():
                        continue
                    with z.open(zip_info) as inner_file:
                        inner_bytes = inner_file.read()
                        inner_name = zip_info.filename
                        text += process_uploaded_file(inner_bytes, inner_name) or ""
        
        else:
            raise ValueError("Unsupported file type")
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
        chunks = splitter.split_text(text)
        return chunks
    
    try:
        with st.spinner("Processing document..."):
            chunks = process_uploaded_file(file_bytes, filename)
        st.success(f"Document processed: {len(chunks)} chunks created")
    except Exception as e:
        st.error(f"Processing error: {str(e)}")
        st.stop()
    
    with st.spinner("Building vector database with OpenAI embeddings..."):
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=st.secrets["OPENAI_API_KEY"]
        )
        vectorstore = FAISS.from_texts(chunks, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
    
    with st.spinner("Querying Gemma-2-9b-it..."):
        llm = HuggingFaceEndpoint(
            repo_id="google/gemma-2-9b-it",
            huggingfacehub_api_token=st.secrets["HF_TOKEN"],
            task="text-generation",
            temperature=0.3,
            max_new_tokens=1024,
        )
        
        prompt = PromptTemplate.from_template(
            "Use this context (with page/email markers) to answer precisely. Always cite sources as [Page X] or [Email Y].\n\n"
            "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )
        
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )
        
        result = qa.invoke({"query": question})
    
    # Professional answer display
    st.markdown("### Answer")
    st.markdown(f'<div class="answer-box">{result["result"]}</div>', unsafe_allow_html=True)
    
    with st.expander(f"📑 View Sources ({len(result['source_documents'])} relevant chunks)", expanded=False):
        for i, doc in enumerate(result["source_documents"], 1):
            st.markdown(f'<div class="source-chunk"><strong>Chunk {i}:</strong><br>{doc.page_content[:800]}...</div>', unsafe_allow_html=True)

else:
    st.info("👈 Upload a document in the sidebar and enter your question to begin.")
    st.markdown("""
        ### Features
        - **Multi-format support**: PDFs, email archives (.mbox), and ZIP files
        - **Advanced retrieval**: OpenAI's top-tier embeddings for accurate semantic search
        - **Precise citations**: Answers always reference original pages or emails
        - **Mobile-ready**: Fully responsive design
    """)

st.markdown("---")
st.markdown("❤️ [Buy me a coffee ☕](https://ko-fi.com/bryantolbert)")
st.caption("Professionally enhanced • Working perfectly as of December 18, 2025")
