# ESILV ChatBot - AI-Powered Student Assistant

An intelligent chatbot system for ESILV (École Supérieure d'Ingénieurs Léonard de Vinci) that provides accurate information about programs, admissions, campus life, and more using Retrieval-Augmented Generation (RAG).

## 🎯 Features

- **Intelligent Intent Routing**: Automatically detects whether users want information or wish to leave contact details
- **Multi-Format Document Support**: Processes `.txt`, `.md`, and `.pdf` files
- **Semantic Search**: Vector-based retrieval finds relevant information across 100+ documents
- **Source Attribution**: Every answer includes citations showing which documents were used
- **Admin Panel**: Upload documents, rebuild index, view contact requests, and manage the system
- **Automated Web Scraping**: Collect and parse content from the ESILV website
- **Real-time Updates**: Index rebuilds without downtime using session state management

## 🏗️ Architecture

```
┌─────────────┐
│   User UI   │
│  (Streamlit)│
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Orchestrator   │  ← Intent detection (Q&A vs Contact)
└────┬────────┬───┘
     │        │
     ▼        ▼
┌─────────┐  ┌──────────────┐
│Retrieval│  │   Contact    │
│ Agent   │  │  Collector   │
└────┬────┘  └──────────────┘
     │
     ▼
┌─────────────────┐
│  VectorStore    │  ← ChromaDB with embeddings
│  (ChromaDB)     │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│   Documents     │  ← 99 TXT + PDFs
│  (data/docs/)   │
└─────────────────┘
```

## 📁 Project Structure

```
ESILV_ChatBot_Assistance_LLM-GenAI/
├── agents/
│   ├── form_agent.py           # Contact collection agent
│   ├── orchestrator.py         # Intent routing logic
│   └── retrieval_agent.py      # Q&A with RAG
├── app/
│   ├── __init__.py
│   ├── admin_panel.py          # Admin interface (upload, rebuild, contacts)
│   └── app.py                  # Main Streamlit application
├── assets/                     # Static files (images, etc.)
├── configs/
│   ├── __init__.py
│   └── config.py               # Configuration loader
├── data/
│   ├── docs/                   # Source documents (TXT, MD, PDF)
│   ├── index/                  # ChromaDB vector index
│   ├── scraping/               # Raw scraped HTML
│   ├── contacts.json           # User contact submissions
│   └── last_scrape.txt         # Scraping metadata
├── rag/
│   ├── index_builder.py        # Document indexing pipeline
│   └── vector_store.py         # ChromaDB wrapper
├── scraping/
│   ├── __init__. py
│   ├── find_urls.py            # URL discovery
│   ├── ingest. py               # Data ingestion
│   ├── parse_html.py           # HTML to text conversion
│   └── scraper.py              # Web scraping orchestrator
├── services/
│   └── llm. py                  # OpenAI API wrapper
├── . env                        # Environment variables (not in repo)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

## 🚀 Installation

### Prerequisites

- Python 3.9+
- OpenAI API key

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ESILV_ChatBot_Assistance_LLM-GenAI.git
   cd ESILV_ChatBot_Assistance_LLM-GenAI
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements. txt
   ```

4. **Configure OpenAI API:**
   
   Create a `.env` file or set environment variable:
   ```bash
   # Windows PowerShell
   $env: OPENAI_API_KEY="your-api-key-here"
   
   # macOS/Linux
   export OPENAI_API_KEY="your-api-key-here"
   ```

5. **Configure the system:**
   
   Edit `config.yaml` with your settings:
   ```yaml
   rag: 
     docs_dir: "data/docs"
     index_dir: "data/index"
     scraping_dir: "data/scraping"
     model:  "gpt-4o-mini"
     embedding_model: "text-embedding-3-small"
   
   scraping:
     base_url: "https://www.esilv.fr"
     start_paths: ["/"]
     max_depth: 3
   ```

## 📊 Usage

### Running the Application

```bash
streamlit run app/app.py
```

The app will be available at `http://localhost:8501`

### Initial Setup

1. **Scrape Website Content** (Admin Panel):
   - Click "Launch collect" to scrape ESILV website
   - Wait for completion (~2-5 minutes)
   - Scraped content saved to `data/docs/`

2. **Build Vector Index** (Admin Panel):
   - Click "Rebuild Index"
   - Wait for indexing (~30 seconds for 100 documents)
   - Index saved to `data/index/`

3. **Start Chatting** (Chat Panel):
   - Ask questions in French about ESILV
   - Get answers with source citations

### Admin Panel Features

#### 1. Web Scraping
- **Purpose**: Automatically collect content from ESILV website
- **Output**: Parsed `.txt` files in `data/docs/`
- **Frequency**: Run when website content updates

#### 2. Document Upload
- **Supported formats**: `.txt`, `.md`, `.pdf`
- **Use case**: Add custom documents (policies, FAQs, guides)
- **Note**: Must rebuild index after upload

#### 3. Index Rebuild
- **When to use**: 
  - After uploading new documents
  - After scraping new content
  - After deleting documents
  - If search results are outdated
- **Process**:  Deletes old collection, creates fresh index
- **Duration**: ~30 seconds for 100 documents

#### 4. Contact Management
- **View**:  All contact requests from users
- **Export**: Download as JSON
- **Clear**: Remove all contacts

### Chat Interface

#### Question & Answer Mode
Ask questions in French: 

**Examples:**
```
Quelles sont les dates de la rentrée ?
Quelles majeures sont disponibles en cycle ingénieur ?
Comment candidater à l'ESILV ?
Combien coûtent les études ? 
Quelles bourses sont disponibles ?
```

**Response includes:**
- Detailed answer from indexed documents
- Source citations (which files were used)
- Response time

#### Contact Collection Mode
Express interest in receiving information:

**Examples:**
```
Je voudrais recevoir plus d'informations
Envoyez-moi des détails sur les admissions
J'aimerais être contacté
```

**System will:**
- Detect contact intent
- Ask for email address
- Confirm submission
- Store in `data/contacts.json`

## 🔧 Configuration

### config.yaml

```yaml
rag:
  docs_dir: "data/docs"           # Document storage
  index_dir: "data/index"         # Vector index storage
  scraping_dir: "data/scraping"   # Raw HTML storage
  model: "gpt-4o-mini"            # OpenAI model for answers
  embedding_model: "text-embedding-3-small"  # Embedding model
  contacts_file: "data/contacts. json"        # Contact storage

scraping:
  base_url: "https://www.esilv.fr"
  start_paths: ["/"]              # Pages to scrape
  max_depth: 3                    # Link depth to follow
  delay:  1. 0                      # Delay between requests (seconds)
```

### Environment Variables

```bash
OPENAI_API_KEY=your-api-key-here  # Required for LLM and embeddings
```

## 📚 Technical Details

### RAG Pipeline

1. **Document Loading**: 
   - Reads files from `data/docs/`
   - Supports `.txt`, `.md`, `.pdf`
   - Extracts text content

2. **Chunking**:
   - Documents stored as-is (no splitting currently)
   - Metadata includes source filename

3. **Embedding**: 
   - Uses OpenAI `text-embedding-3-small`
   - 1536-dimensional vectors
   - Stored in ChromaDB

4. **Retrieval**:
   - Semantic search with cosine similarity
   - Returns top-8 most relevant chunks
   - Includes source metadata

5. **Generation**:
   - Context sent to `gpt-4o-mini`
   - System prompt ensures accurate, complete answers
   - Sources appended to response

### Intent Routing

**Keyword-based detection:**
- **Retrieval**: Questions, information requests
- **Contact**: "m'envoyer", "me contacter", "recevoir des informations"

**Process:**
```
User Input → Orchestrator → Intent Detection
                ↓
         ┌──────┴──────┐
         ▼             ▼
    Retrieval      Contact
     Agent        Collector
         ↓             ↓
    Answer +      Email Form
    Sources
```

## 🐛 Troubleshooting

### "No documents found"
**Cause**: Index is empty or corrupted  
**Fix**: Admin Panel → Rebuild Index

### "Text is None" warnings
**Cause**: Corrupted ChromaDB index  
**Fix**:  
1. Stop Streamlit
2. Delete `data/index/` folder
3. Restart and rebuild

### "Aucune information pertinente trouvée"
**Cause**: Information not in indexed documents  
**Fix**: 
1. Check if document exists in `data/docs/`
2. If missing, scrape or upload it
3. Rebuild index

### Unicode errors on Windows
**Cause**: Console encoding issues  
**Fix**: Already handled in code with UTF-8 forcing

### Slow query performance
**Cause**: Large index or slow embeddings  
**Fix**: 
- Reduce `k` value in retrieval (default: 8)
- Use faster embedding model
- Chunk large documents

## 📈 Performance

- **Index build time**: ~30s for 100 documents
- **Query latency**: 2-5 seconds (embedding + LLM)
- **Memory usage**: ~500MB (ChromaDB + embeddings)
- **Disk usage**: ~50MB (index) + document size

## 🔐 Security Notes

- **API Keys**: Never commit `.env` or `config.yaml` with keys
- **Contact Data**: `contacts.json` contains user emails - handle securely
- **Admin Access**: No authentication currently - add in production

## 🚧 Future Improvements

- [ ] Add authentication for admin panel
- [ ] Implement document chunking for large files
- [ ] Add conversational memory (multi-turn chat)
- [ ] Support more file formats (DOCX, HTML)
- [ ] Add analytics dashboard
- [ ] Implement feedback collection (thumbs up/down)
- [ ] Add multi-language support (English, French)
- [ ] Deploy to cloud (Streamlit Cloud, Heroku, AWS)

## 📄 License

This project is for educational purposes as part of ESILV coursework. 
