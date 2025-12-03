# ESILV Smart Assistant

An intelligent chatbot dedicated to the ESILV engineering school. It supports:
- Factual Q&A using RAG over ESILV website and internal docs
- Structured interactions for collecting contact details (name, email, phone)
- Multi-agent coordination (retrieval agent, form-filling agent, orchestrator)
- Local deployment with Ollama or cloud deployment on Google Cloud (Vertex AI)
- Streamlit front-end for chat, document uploads, and admin visualization

## Installation
After cloning the repository
'''bash
git clone $URL
'''

Please install the required Python environment with
-for Linux and MacOS
'''bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
'''
-for Windows
'''bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
'''

Then install Ollama: https://ollama.com/download
And any model you want, for example Mistral :
'''bash
ollama pull mistral
'''

⚠️ If you are not using mistral, go in config.py and change this line:
'''bash
OLLAMA_MODEL = "mistral"
'''

In your terminal, make sure to be at the root of your project, and that your environment is running. Then enter this command:
'''bash
streamlit run app.by
'''

The chatbot page should open in your browser.