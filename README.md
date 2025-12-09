# ESILV Smart Assistant

An intelligent chatbot dedicated to the ESILV engineering school. It supports:
- Factual Q&A using RAG over ESILV website and internal docs
- Structured interactions for collecting contact details (name, email, phone)
- Multi-agent coordination (retrieval agent, form-filling agent, orchestrator)
- Local deployment with Ollama or cloud deployment on Google Cloud (Vertex AI)
- Streamlit front-end for chat, document uploads, and admin visualization

## To-do list ⭕✅
✅ Setup the chatbot with the streamlit frontend
✅ RAG agent
✅ Form agent
✅ Orchestrator agent
✅ Admin page
⭕ Save vectorstore
⭕ Parent/Children LLMClient class
⭕ Scraping agent
⭕ Agenda sub-agent ?
⭕ Web search agent
⭕ JSON schema as parameter
⭕ Handling updates in admin page



about form agent: JSON schema as a parameter (we have to check if it is possible for ollama & vertex)
to save the embeddings instead of reloading it each time
make two separates clients one vertex and one ollama 
for RAG: web searcher & web scrapping 
for the admin page: what if i upload again the same info that i already have, let make some thing it asks the user "do u want to update this document" , and then we check if we want to update it or just add a new one