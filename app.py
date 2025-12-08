import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os

# NOTE: Do NOT hard-code your HuggingFace token in this file.
# Use Streamlit secrets (/.streamlit/secrets.toml) or the HF_TOKEN environment variable.

# ========================= CONFIG =========================
st.set_page_config(page_title="AskMyPDFs", page_icon="📚", layout="centered")

# ========================= SIDEBAR =========================
with st.sidebar:
    st.title("📚 AskMyPDFs")
    st.caption("Multi‑PDF Question Answering")

    st.markdown("---")
    st.markdown("### 💡 How to Use")
    st.markdown(
        """
        1. Upload one or more PDFs
        2. Ask any question about them
        3. Get answers with citations
        4. Filter by specific documents
        """
    )

    st.markdown("---")
    st.markdown("### ☕ Support This Project")
    st.markdown("If you find this tool helpful, consider buying me a coffee!")

    # Ko-fi button
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
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 🔧 Tech Stack")
    st.markdown(
        """
        - **LLM:** Gemma-2-9B
        - **Embeddings:** MiniLM-L6-v2
        - **Vector DB:** FAISS
        - **Framework:** LangChain
        """
    )

# ========================= MAIN =========================
st.title("📚 Ask Questions Across Your PDFs")
st.caption("Upload multiple PDFs and get AI-powered answers with source citations")

# Inputs
pdfs = st.file_uploader("Upload one or more PDFs", type="pdf", accept_multiple_files=True)
question = st.text_input(
    "Ask anything across your PDFs",
    placeholder="e.g., Compare introductions • Summarize references • What is said on page 42 of doc2?",
)

# Helpers
@st.cache_resource(show_spinner="Extracting text from PDFs...")
def process_pdfs(uploaded_files):
    """Extract text from PDFs and annotate pages.

    Returns:
        tuple[list[str], list[tuple[str, int, int]]]: (chunks, doc_index)
        doc_index entries: (filename, num_pages, num_chunks)
    """
    all_chunks: list[str] = []
    doc_index: list[tuple[str, int, int]] = []

    for uploaded_file in uploaded_files:
        try:
            reader = PdfReader(uploaded_file)
            text_with_pages = ""

            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_with_pages += f"\n\n[{uploaded_file.name} – Page {i+1}]\n{page_text}"
                except Exception as exc:  # keep going if a page fails
                    st.warning(f"Could not extract page {i+1} from {uploaded_file.name}: {exc}")
                    continue

            if not text_with_pages.strip():
                st.error(f"No text could be extracted from {uploaded_file.name}")
                continue

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=400,
                separators=["\n\n", "\n", " ", ""],
                keep_separator=True,
            )

            chunks = splitter.split_text(text_with_pages)
            all_chunks.extend(chunks)
            doc_index.append((uploaded_file.name, len(reader.pages), len(chunks)))

        except Exception as exc:
            st.error(f"Error processing {uploaded_file.name}: {exc}")
            continue

    return all_chunks, doc_index


@st.cache_resource(show_spinner="Building vector database...")
def create_vectorstore(chunks):
    """Create a FAISS vector store from text chunks using Hugging Face embeddings."""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        vectorstore = FAISS.from_texts(chunks, embeddings)
        return vectorstore
    except Exception as exc:
        st.error(f"Error creating vector store: {exc}")
        raise


def build_qa_chain(vectorstore, filter_doc=None):
    """Build the RetrievalQA chain. Requires HF token in Streamlit secrets or HF_TOKEN env var."""
    try:
        # Prefer Streamlit secrets; fall back to environment variable
        hf_token = None
        try:
            hf_token = st.secrets.get("HF_TOKEN")
        except Exception:
            # st.secrets may not be available in some runtime contexts
            hf_token = None

        if not hf_token:
            hf_token = os.environ.get("HF_TOKEN")

        if not hf_token:
            st.error("HuggingFace token not found. Add HF_TOKEN to Streamlit secrets or set the HF_TOKEN environment variable.")
            st.stop()

        llm = HuggingFaceEndpoint(
            repo_id="google/gemma-2-9b-it",
            huggingfacehub_api_token=hf_token,
            temperature=0.3,
            max_new_tokens=1024,
        )

        prompt_template = (
            "You are an expert assistant analyzing multiple PDFs.\n"
            "Use the following context (with file names and page numbers) to answer concisely.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Instructions:\n"
            "- Always cite both file name and page numbers, e.g. [doc1.pdf – Page 42].\n"
            "- If not found, say \"Not found in the documents.\"\n"
            "- Keep the answer clear and professional.\n\n"
            "Answer:"
        )

        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        # Create retriever; if filtering by a specific document, wrap the base retriever
        if filter_doc and filter_doc != "All PDFs":
            base_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

            def filtered_get_relevant_documents(query):
                docs = base_retriever.get_relevant_documents(query)
                filtered = [doc for doc in docs if filter_doc in doc.page_content]
                return filtered[:6]

            # Monkey-patch only the method we need
            base_retriever.get_relevant_documents = filtered_get_relevant_documents
            retriever = base_retriever
        else:
            retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT},
        )

        return qa_chain

    except Exception as exc:
        st.error(f"Error building QA chain: {exc}")
        raise


# Main execution
if pdfs and question:
    try:
        with st.status("Processing PDFs...", expanded=False) as status:
            chunks, doc_index = process_pdfs(pdfs)

            if not chunks:
                st.error("No text could be extracted from the uploaded PDFs. Please check your files.")
                st.stop()

            st.write("Extracted chunks:")
            for name, pages, chunks_count in doc_index:
                st.write(f"- {name}: {pages} pages → {chunks_count} chunks")

            vectorstore = create_vectorstore(chunks)
            st.write("✅ Vector database ready")

            # Dropdown filter
            doc_names = ["All PDFs"] + [name for name, _, _ in doc_index]
            filter_choice = st.selectbox("Restrict search to:", doc_names, key="doc_filter")

            qa_chain = build_qa_chain(vectorstore, filter_choice)

            st.write("🤔 Querying the model...")
            result = qa_chain.invoke({"query": question})

            answer = result.get("result")
            sources = result.get("source_documents", [])

            status.update(label="✅ Done!", state="complete", expanded=False)

        # Display answer
        st.success("Answer")
        st.markdown(answer)

        # Show sources
        if sources:
            with st.expander(f"📄 Show sources ({len(sources)} chunks used)"):
                for i, doc in enumerate(sources, 1):
                    preview = doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else "")
                    st.caption(f"Source {i}:")
                    st.text(preview)
                    st.divider()

    except Exception as exc:
        st.error(f"An error occurred: {exc}")
        st.info("Please try again or check your HuggingFace token configuration.")

elif pdfs and not question:
    st.info("✅ PDFs loaded! Now type your question above.")
else:
    st.info("👆 Upload one or more PDFs and ask your question!")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#888;'>"
    "Made with ❤️ by Bryant Olbert"
    "</p>",
    unsafe_allow_html=True,
)
