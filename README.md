                AI VIDEO ASSISTANT
                       │
          ┌────────────┴────────────┐
          │                         │
   ➕ Process New              📂 Open Existing
          │                         │
    YouTube URL              Video ID + URL
          │                         │
          ▼                         ▼
       FastAPI                No processing
          │                         │
          ▼                         │
      Pinecone                       │
          │                         │
          └────────────┬────────────┘
                       ▼
                 🎥 Video
                       │
                       ▼
                 💬 Ask Video
                       │
                       ▼
               RAG + LLM Answer
                       │
                       ▼
                  Timestamps