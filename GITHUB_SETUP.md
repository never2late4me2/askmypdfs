# 🚀 GitHub Setup Guide - Copy & Paste Commands

## Step 1: Create GitHub Repository

### Repository Information (Copy & Paste)

**Repository Name:**
```
askmypdfs
```

**Description:**
```
Multi-PDF Question Answering System with AI - Upload PDFs and ask questions across documents using RAG (Retrieval-Augmented Generation) powered by LangChain and HuggingFace Gemma-2-9B
```

**Topics/Tags (comma-separated):**
```
streamlit, pdf, langchain, ai, rag, question-answering, huggingface, faiss, nlp, machine-learning, python, gemma, document-analysis, vector-database, embeddings
```

**Settings:**
- ✅ Public (or Private if you prefer)
- ✅ Add a README file: **NO** (we have our own)
- ✅ Add .gitignore: **NO** (we have our own)
- ✅ Choose a license: **MIT License** (recommended)

---

## Step 2: Push Code to GitHub

### Option A: Using Command Line (Recommended)

**Copy and paste these commands one by one:**

```bash
# Navigate to the project folder
cd AskMyPDFs_Fixed

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Multi-PDF QA system with Ko-fi monetization

✅ Fixed all import errors for latest LangChain
✅ Implemented working document filter
✅ Added comprehensive error handling
✅ Configured Ko-fi monetization (ko-fi.com/bryantolbert)
✅ Added HuggingFace token support
✅ Complete deployment documentation
✅ Production-ready for Streamlit Cloud"

# Set main branch
git branch -M main

# Add your GitHub repository (REPLACE WITH YOUR REPO URL)
git remote add origin https://github.com/YOUR_USERNAME/askmypdfs.git

# Push to GitHub
git push -u origin main
```

**⚠️ Important:** Replace `YOUR_USERNAME` with your actual GitHub username!

---

### Option B: Using GitHub Desktop

1. Open **GitHub Desktop**
2. Click **File** → **Add Local Repository**
3. Browse to `AskMyPDFs_Fixed` folder
4. Click **Create Repository**
5. Set commit message:
   ```
   Initial commit: Multi-PDF QA system with Ko-fi monetization
   ```
6. Click **Commit to main**
7. Click **Publish repository**
8. Choose repository name: `askmypdfs`
9. Add description (see above)
10. Click **Publish Repository**

---

### Option C: Upload via GitHub Web Interface

1. Go to **github.com** and create new repository
2. Name it: `askmypdfs`
3. Add description (see above)
4. Click **Create repository**
5. Click **uploading an existing file**
6. Drag all files from `AskMyPDFs_Fixed` folder
7. **⚠️ IMPORTANT:** Do NOT upload `.streamlit/secrets.toml` (contains your token)
8. Set commit message:
   ```
   Initial commit: Multi-PDF QA system
   ```
9. Click **Commit changes**

---

## Step 3: Configure Repository Settings

### Add Repository Description

Go to your repository → Click **⚙️ Settings** → Under "About", click **⚙️ Edit**

**Description:**
```
🤖 AI-powered multi-PDF question answering system using RAG, LangChain, and HuggingFace Gemma-2-9B
```

**Website:**
```
https://your-app-name.streamlit.app
```
*(Add this after deployment)*

**Topics:**
```
streamlit
pdf
langchain
ai
rag
question-answering
huggingface
faiss
nlp
machine-learning
python
gemma
document-analysis
vector-database
embeddings
```

### Update README Badge (Optional)

Add this to the top of your README.md:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20Me-ff5e5b?logo=ko-fi&logoColor=white)](https://ko-fi.com/bryantolbert)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

## Step 4: Verify Upload

### Check that these files are in your repository:

```
✅ app.py
✅ app_with_sidebar_kofi.py
✅ requirements.txt
✅ README.md
✅ QUICKSTART.md
✅ KOFI_SETUP.md
✅ CHANGES_SUMMARY.md
✅ VERIFICATION_REPORT.md
✅ CHECKLIST.md
✅ .gitignore
✅ .streamlit/config.toml
✅ .streamlit/secrets.toml.example
❌ .streamlit/secrets.toml (should NOT be uploaded - contains your token)
```

### If you accidentally uploaded secrets.toml:

**Remove it immediately:**

```bash
git rm --cached .streamlit/secrets.toml
git commit -m "Remove secrets file"
git push
```

Then go to **HuggingFace** and **regenerate your token** for security!

---

## Step 5: Deploy to Streamlit Cloud

### Copy & Paste Deployment Steps:

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"**
3. Select your repository: `YOUR_USERNAME/askmypdfs`
4. Branch: `main`
5. Main file path: `app.py`
6. Click **"Advanced settings"**
7. Under **"Secrets"**, paste:

```toml

```

8. Click **"Save"**
9. Click **"Deploy!"**
10. Wait 2-3 minutes for deployment

---

## 📋 Commit Message Template

If you need to make updates, use this commit message format:

```
[TYPE] Brief description

Detailed changes:
- Change 1
- Change 2
- Change 3
```

**Types:**
- `[FIX]` - Bug fixes
- `[FEAT]` - New features
- `[DOCS]` - Documentation updates
- `[STYLE]` - UI/styling changes
- `[REFACTOR]` - Code refactoring
- `[TEST]` - Testing updates

**Example:**
```
[FEAT] Add support for DOCX files

Detailed changes:
- Added python-docx to requirements
- Updated file uploader to accept .docx
- Added DOCX text extraction function
```

---

## 🎯 Quick Reference

### Your Repository URLs:

**GitHub Repository:**
```
https://github.com/YOUR_USERNAME/askmypdfs
```

**Streamlit App (after deployment):**
```
https://YOUR_USERNAME-askmypdfs-app-xxxxx.streamlit.app
```

**Ko-fi Page:**
```
https://ko-fi.com/bryantolbert
```

### Your Credentials:

**HuggingFace Token:** (in `.streamlit/secrets.toml` - DO NOT COMMIT)
```
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
```

---

## 🆘 Troubleshooting

### "Permission denied" error:
```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/YOUR_USERNAME/askmypdfs.git
```

### "Repository not found" error:
- Check your GitHub username is correct
- Make sure the repository exists
- Try using personal access token

### "Secrets file uploaded by mistake":
```bash
git rm --cached .streamlit/secrets.toml
git commit -m "Remove secrets"
git push
# Then regenerate your HuggingFace token!
```

### "Deployment fails on Streamlit Cloud":
- Check requirements.txt is in root
- Verify secrets are added in Streamlit Cloud
- Check deployment logs for specific errors

---

## ✅ Success Checklist

- [ ] GitHub repository created
- [ ] All files pushed (except secrets.toml)
- [ ] Repository description added
- [ ] Topics/tags added
- [ ] Deployed to Streamlit Cloud
- [ ] Secrets configured in Streamlit
- [ ] App is live and working
- [ ] Ko-fi button tested
- [ ] Repository URL shared

---

**Ready to push?** Copy the commands from **Step 2, Option A** above! 🚀
