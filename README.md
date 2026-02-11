# Hogwarts Oracle Pro: Closed-Domain RAG System 🪄

This project implements a professional **RAG (Retrieval-Augmented Generation)** architecture designed to query specific documentation with 100% accuracy. Using the first two books of the Harry Potter saga as a local knowledge base, the system demonstrates how to restrict an LLM (GPT-4o-mini) to only provide information found within the provided sources.

## 🚀 Key Technical Features

* **Knowledge Boundary Enforcement:** Custom system prompts (Guardrails) prevent the AI from using external knowledge or hallucinating details from later books not present in the database.
* **Vector Embeddings & Persistence:** Uses `OpenAIEmbeddings` to transform text into high-dimensional vectors, stored in a local **Qdrant** collection for fast semantic retrieval.
* **Recursive Chunking:** Implements `RecursiveCharacterTextSplitter` with overlapping (1000 chars, 150 overlap) to maintain semantic context between fragments.
* **Source Transparency:** Every response includes the specific filenames (`source metadata`) used by the AI to generate the answer.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Framework:** FastAPI (Swagger/OpenAPI UI)
* **AI Orchestration:** LangChain
* **Vector Database:** Qdrant (Local Persistent Mode)
* **LLM:** OpenAI GPT-4o-mini

## 📊 Proof of Concept (RAG in Action)

The system is designed to prove its "Closed-World" reliability.

### Case 1: Knowledge Within Scope
When asked about Neville Longbottom (present in books 1 & 2), the system provides a detailed answer and cites the source files.
![Retrieval Success](img/success_query.png)

### Case 2: Out of Scope Prevention
When asked about characters or events from later books (e.g., Luna Lovegood or Sirius Black), the system strictly follows the guardrails and refuses to answer.
![Guardrail Prevention](img/guardrail_check.png)

## 📁 Project Structure
* `ingesta.py`: Script for loading, splitting, and vectorizing PDF documents into Qdrant.
* `main.py`: FastAPI application serving the RAG logic and the restricted LLM prompt.
* `db_harry_potter/`: Local persistent vector storage.

---
*Note: This architecture is directly applicable to corporate environments for querying internal manuals, legal documents, or private FAQs while ensuring data security and reliability.*
