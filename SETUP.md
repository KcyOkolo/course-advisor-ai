# Installation Instructions for COURSE-ADVISOR-AI

## Prerequisites:
The following must be installed before hand:
- Python 3.9+
- pip
- Git

## Installation Steps
* note: You can access course advisor ai without installing locally! temporary public url:  https://6c99bf50a0f08caefe.gradio.live 

* To install locally:
1. Clone repository:
* git clone https://github.com/KcyOkolo/course-assistant-ai.git
* cd course-assistant-ai

2. Create virtual environment to isolate project dependencies: 
* python3 -m venv venv
* source venv/bin/activate

3. Install all dependencies: 
* pip install -r requirements.txt

This will install:
* gradio - Used to build the UI
* anthropic - Claude API Client
* sentence-transformers - Text embedding models
* faiss-cpu - Indexing and Vector similarity search
* pyumupdf - PDF processing

To verify installation: 
* python test_setup.py


4. Set Up API Key:
* To use my API key:
Email me at kyo3@duke.edu for access. My API key is also written at beginning of my submmited self-evaluation.

* To use your own key:
Go to console.anthropic.com, sign up and navigate to "API Keys", create a new key 

* Adding the key:
Create `.env` file in root directory and write ANTHROPIC_API_KEY= {insert API key here} 

5. Run the app: on command line at root directory: python app.py 

* Sample Syllabi :
I have included sample syllabi in data/duke_syllabi
These syllabi were not used to train. No training or finetuning was done in this project
They are only for testing/providing input to RAG (if interacting on command line level)
Feel free to add your own syllabi to the path specified above