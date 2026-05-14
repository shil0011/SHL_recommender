# SHL Assessment Recommender Agent

A production-ready conversational agent built with FastAPI and RAG (Retrieval-Augmented Generation) to help recruiters identify the best SHL assessments for their hiring needs.

## Features
- **Deterministic Routing**: Uses an intent detection layer to route queries to specialized modules.
- **RAG Architecture**: Recommendations are grounded in the official SHL product catalog.
- **Guardrails**: Protects against off-topic queries and prompt injections.
- **Stateless API**: Complies with the requirement to pass full conversation history.

## Tech Stack
- **Backend**: FastAPI, Python
- **LLM Orchestration**: LangChain
- **Vector DB**: FAISS
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Scraping**: BeautifulSoup4

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Scrape Catalog**:
   ```bash
   python scraper/scrape.py
   ```

3. **Set Environment Variables**:
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_key_here
   ```

4. **Run Server**:
   ```bash
   python -m app.main
   ```

## API Endpoints
- `GET /health`: Returns service status.
- `POST /chat`: Receives conversation history and returns a natural language reply with assessment recommendations.

## Architecture Deep Dive

### Why this is better than a pure LLM chatbot?
Traditional LLM chatbots ("vibe-coding") are prone to hallucinations, especially with specific product catalogs. This architecture is superior because:
1. **Groundedness**: We use a Vector Database (FAISS) as the source of truth. The LLM only acts as a natural language interface for the retrieved data.
2. **Predictability**: The intent router ensures that if a user asks for a comparison, we use a comparison logic, rather than letting the LLM guess.
3. **Safety**: The guardrail layer acts as a firewall, filtering malicious or irrelevant inputs before they reach the core logic.
4. **Scalability**: New assessments can be added to the catalog and re-indexed without retraining or re-prompting the LLM.

## Evaluation
Run tests with:
```bash
pytest tests/test_chat.py
```
