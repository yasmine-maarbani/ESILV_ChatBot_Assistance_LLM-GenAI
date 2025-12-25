# ESILV Smart Assistant

An intelligent chatbot dedicated to the ESILV engineering school. It supports:
- Factual Q&A using RAG over ESILV website and internal docs
- Structured interactions for collecting contact details (name, email, phone)
- Multi-agent coordination (retrieval agent, form-filling agent, orchestrator)
- Local deployment with Ollama or cloud deployment on Google Cloud (Vertex AI)
- Streamlit front-end for chat, document uploads, and admin visualization


## To-do list ❌✅
✅ Setup the chatbot with the streamlit frontend <br>
✅ RAG agent <br>
✅ Form agent <br>
✅ Orchestrator agent <br>
✅ Admin page <br>
✅ Display answering time <br>
✅ Save vectorstore <br>
✅ Scraping button <br>
✅ RAG handles .pdf files
✅ Parent/Children LLMClient class <br>
✅ Automation of weekly scraping on the website and daily scraping on agenda <br>
❌ Web search agent <br>
❌ JSON schema as parameter <br>
❌ Handling updates in admin page <br>
❌ What is our evaluation strategy ? (cf teacher's instructions)
⚠️ Update instructions in README.md
⚠️ Comment and clean code
🗨️ "Teams are encouraged to use LangChain, LangGraph, Streamlit, and FastAPI for orchestration and UI" -> ask him about Chroma, ...

❌❌❌ Write report

## Instructions

```bash
# Clone the GitHub repository of the project
git clone https://github.com/yasmine-maarbani/ESILV_ChatBot_Assistance_LLM-GenAI.git

# Install python environment
python -m venv .venv
source .venv/bin/activate # On Linux/MacOS, if you are working on Windows: .venv/Scripts/activtate (if error, try:)
pip install -r requirements.txt
```

To run the front-end and access the ChatBot:
```bash
python -m streamlit run app/app.py
```
### Set up LLM environment
In .env.example and/or configs/config.py, change your settings to have either an Ollama model, or use Vertex.


### To upload new documents (MAYBE PUT IMAGES TO ILLUSTRATE THE TUTO)

Of course, you can manually put your documents in data/docs, but it won't be integrated into the vector store of the RAG. <br>
Another way to upload your documents is in the Admin tab of the chatbot; there you can upload your document using the UI. <br>
Whether you uploaded your document manually or with the UI, you should still click on the "Rebuild Index" button to add your new documents to the database of the RAG. The Chatbot is automatically updated, therefore you can verify your actions by asking a specific question in the main tab.

### To manually force collection of data from esilv.fr (ILLUSTRATION TOO)

In the Admin tab, there is a button "Launch collect" that run the scraping job of the website pages. The purpose of such button is to test and debbug this program, and also for exceptional occasion where an Administrator must update the retriever database between weekly call (e.g. if the website is down during the automatic collect, or an error was found on one page and has been corrected).