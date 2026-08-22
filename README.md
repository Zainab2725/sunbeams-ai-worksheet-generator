# 📚 Sunbeams AI Worksheet Generator

An AI-powered system that automatically extracts textbook content, processes Urdu/English educational text, and generates ready-to-print, curriculum-aligned worksheets for primary classrooms.

## ✨ Features

*  Extract content from textbook PDFs
*  Process both Urdu and English text
*  Clean and structure extracted textbook content
*  Use RAG for curriculum-grounded worksheet generation
*  Generate worksheets using LLMs
*  Store and retrieve textbook knowledge using ChromaDB/FAISS
*  Generate printable PDF worksheets
*  Support Urdu font rendering with **Jameel Noori Nastaliq**
*  Provide an interactive Streamlit interface for teachers

---

## 🏗️ Project Structure

```text
sunbeams-ai-worksheet-generator/
│
├── data/
│   └── # Standard textbook PDFs and reference files
│
├── src/
│   ├── data_pipeline/
│   │   └── # PDF extraction, text cleaning, and Urdu processing
│   │
│   ├── rag_engine/
│   │   └── # Text chunking, vector database, retrieval, and LLM prompts
│   │
│   ├── pdf_generator/
│   │   └── # Printable worksheet generation and Urdu font rendering
│   │
│   └── ui/
│       └── # Streamlit web interface
│
├── docs/
│   └── # Test cases, QA checklists, and user guides
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 👥 Module Breakdown

| Module            | Location             | Core Responsibilities                                                                        |
| ----------------- | -------------------- | -------------------------------------------------------------------------------------------- |
| **Data Pipeline** | `src/data_pipeline/` | Extract text from Sunbeams PDFs, clean textbook content, and process Urdu/English scripts    |
| **RAG Engine**    | `src/rag_engine/`    | Implement text chunking, ChromaDB/FAISS retrieval, and LLM prompt logic                      |
| **PDF Generator** | `src/pdf_generator/` | Convert generated worksheets into printable PDFs with proper margins and Urdu font rendering |
| **UI Frontend**   | `src/ui/`            | Build the interactive Streamlit dashboard for teachers                                       |

---

## 🔄 System Workflow

```text
Textbook PDF
     ↓
PDF Text Extraction
     ↓
Text Cleaning & Urdu/English Processing
     ↓
Text Chunking
     ↓
Vector Database
(ChromaDB / FAISS)
     ↓
RAG Retrieval
     ↓
LLM Worksheet Generation
     ↓
Worksheet Formatting
     ↓
Printable PDF
     ↓
Teacher
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Zainab2725/sunbeams-ai-worksheet-generator.git
cd sunbeams-ai-worksheet-generator
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Example
OPENAI_API_KEY=your_api_key_here
```

> Never commit `.env` or API keys to GitHub.

### 5. Run the Application

Once the Streamlit interface is implemented:

```bash
streamlit run src/ui/app.py
```

---

## 🧩 Development Guidelines

### 🌿 Branching

Do not push unfinished or broken code directly to `main`.

Create a separate branch for your feature:

```bash
git checkout -b feature/your-feature-name
```

Example:

```bash
git checkout -b feature/pdf-generator
```

### 🔄 Pull Before Push

Before starting work and before pushing your changes:

```bash
git pull origin main
```

### 🔐 Environment Variables

Keep API keys and secrets inside `.env`.

Never commit:

```text
.env
*.key
*.pem
credentials.json
```

Make sure these are included in `.gitignore`.

### 🧪 Test Your Changes

Before creating a pull request, make sure your code:

* Runs without errors
* Does not break existing functionality
* Handles Urdu and English text correctly where applicable
* Follows the existing project structure
* Includes appropriate test cases when necessary

---

## 📂 Where Should I Work?

Choose the folder corresponding to your assigned module:

```text
Data extraction / Urdu processing
        ↓
src/data_pipeline/

RAG / ChromaDB / FAISS / LLM prompts
        ↓
src/rag_engine/

PDF / worksheet formatting / Urdu fonts
        ↓
src/pdf_generator/

Streamlit interface
        ↓
src/ui/
```

Avoid modifying another team's module unless it is necessary and discussed with the team.

---

## 🤝 Git Workflow

A recommended workflow:

```bash
# Get the latest changes
git pull origin main

# Create your feature branch
git checkout -b feature/your-feature

# Make your changes

# Check your changes
git status

# Stage changes
git add .

# Commit
git commit -m "Add your feature description"

# Push your branch
git push origin feature/your-feature
```

Then create a Pull Request to merge your branch into `main`.

---

## 📌 Important Notes

* Keep textbook/reference files inside `data/`.
* Keep reusable documentation inside `docs/`.
* Keep module-specific implementation inside the appropriate `src/` folder.
* Do not commit API keys or private credentials.
* Do not push broken code directly to `main`.
* Keep commits small and descriptive.
* Test your changes before creating a Pull Request.

---

## 🎯 Project Goal

The goal of **Sunbeams AI Worksheet Generator** is to reduce the time teachers spend manually creating worksheets by transforming curriculum-approved textbook content into structured, relevant, and printable educational material.

> **Textbook → AI → Worksheet → Classroom**

---

## 📜 License

This project is intended for educational and development purposes.
