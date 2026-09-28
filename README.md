# AI Video Assistant Architecture

## 📊 System Flowchart (Mermaid)

```mermaid
graph TD
    %% Main Entry
    A[AI VIDEO ASSISTANT] --> B[➕ Process New<br>YouTube URL / ID]
    A --> C[📂 Open Existing<br>Video ID + URL]

    %% Process New Path
    B --> D[FastAPI Backend]
    D --> E[(Pinecone Vector DB)]
    E --> F[🎥 Video Environment]

    %% Open Existing Path
    C --> G[No Processing Required]
    G --> F

    %% Interaction Path
    F --> H[💬 Ask Video]
    H --> I[RAG + LLM Generation]
    I --> J[⏱️ Timestamps & Answers]

    %% Styling
    style A fill:#4F46E5,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#059669,stroke:#333,stroke-width:1px,color:#fff
    style E fill:#DC2626,stroke:#333,stroke-width:1px,color:#fff
    style F fill:#2563EB,stroke:#333,stroke-width:1px,color:#fff
```

---

## ⚙️ Technical Component Breakdown

*   **FastAPI**: Serves as the core backend API layer. It handles incoming YouTube URLs, downloads/extracts audio transcripts, and coordinates the data pipeline asynchronously.
*   **Pinecone**: A high-performance vector database used to store text embeddings of the video transcripts. It enables semantic search, allowing the system to quickly retrieve relevant video segments.
*   **RAG + LLM**: Retrieval-Augmented Generation. When a user asks a question, the system queries Pinecone for the most relevant transcript segments, injects them into the LLM context, and generates highly accurate answers grounded in the video's content.

---

## 🗺️ User Journey

1.  **Ingestion**: The user either submits a new YouTube link to be processed by the pipeline or opens a previously indexed video instantly using its unique ID.
2.  **Interaction**: Once the video is loaded into the active environment, the user types a natural language question about the content.
3.  **Insight**: The assistant returns an answer backed by **clickable timestamps**, allowing the user to jump directly to the exact moment in the video where the information was spoken.
