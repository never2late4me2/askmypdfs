# 📚 AskMyPDFs - Multi-PDF Question Answering System

A Streamlit application that allows users to upload multiple PDF documents and ask questions across them using RAG (Retrieval-Augmented Generation) powered by LangChain and HuggingFace.

## Features

- ✅ **Multi-PDF Support**: Upload and query multiple PDF documents simultaneously
- ✅ **Source Citations**: Answers include file names and page numbers
- ✅ **Document Filtering**: Restrict searches to specific PDFs
- ✅ **Advanced RAG**: Uses FAISS vector database and Gemma-2-9B LLM
- ✅ **Error Handling**: Comprehensive error handling for robust operation

## Fixed Issues

This version fixes the following deployment issues from the original code:

1. ✅ **Updated Imports**: Fixed deprecated LangChain imports
   - Changed `langchain_text_splitters` → `langchain.text_splitter`
   - Changed `langchain_community.embeddings.HuggingFaceEmbeddings` → `langchain_huggingface.HuggingFaceEmbeddings`
   - Changed `langchain_community.llms.HuggingFaceEndpoint` → `langchain_huggingface.HuggingFaceEndpoint`

2. ✅ **Fixed Document Filtering**: Implemented proper document filtering using custom retriever

3. ✅ **Added Error Handling**: Comprehensive try-catch blocks for all operations

4. ✅ **Environment Fallback**: Support for both `st.secrets` and environment variables

5. ✅ **PDF Extraction**: Better handling of empty pages and extraction failures

6. ✅ **Requirements File**: Complete `requirements.txt` for deployment

## Deployment Instructions

### Option 1: Deploy to Streamlit Cloud (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository, branch, and `app.py`
   - Click "Advanced settings" → "Secrets"
   - Add your HuggingFace token:
     ```toml
     HF_TOKEN = "your_huggingface_token_here"
     ```
   - Click "Deploy"

3. **Get Your HuggingFace Token**:
   - Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Create a new token (read access is sufficient)
   - Copy and paste it into Streamlit secrets

### Option 2: Run Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Secrets**:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml and add your HuggingFace token
   ```

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Technical Stack

- **Frontend**: Streamlit
- **PDF Processing**: pypdf
- **Text Splitting**: LangChain RecursiveCharacterTextSplitter
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS
- **LLM**: google/gemma-2-9b-it (via HuggingFace)
- **Framework**: LangChain

## Usage

1. Upload one or more PDF files
2. Type your question in the text input
3. Optionally filter to search within a specific document
4. View the answer with source citations
5. Expand "Show sources" to see the retrieved chunks

## Troubleshooting

### Common Issues:

**"HuggingFace token not found"**
- Make sure you've added `HF_TOKEN` to your secrets (Streamlit Cloud) or `.streamlit/secrets.toml` (local)

**"No text could be extracted"**
- Some PDFs are image-based and require OCR
- Try a different PDF or use a text-based PDF

**"Error creating vector store"**
- This usually means the embeddings model failed to load
- Check your internet connection and HuggingFace access

**Deployment fails on Streamlit Cloud**
- Check the logs for specific errors
- Ensure `requirements.txt` is in the root directory
- Verify your HuggingFace token is valid

## File Structure

```
.
├── app.py                          # Main application
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── config.toml                # Streamlit configuration
│   └── secrets.toml.example       # Secrets template
├── .gitignore                     # Git ignore file
└── README.md                      # This file
```

## Credits

Made with ❤️ by bryantolbert  
Updated: December 07, 2025  
Fixed and optimized for deployment
