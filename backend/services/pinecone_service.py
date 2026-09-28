from pinecone import Pinecone

from backend.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME
)

from backend.services.embedding_service import (
    create_embedding
)


# --------------------------------------------------
# Pinecone Client
# --------------------------------------------------

pc = Pinecone(
    api_key=PINECONE_API_KEY
)


# --------------------------------------------------
# Pinecone Index
# --------------------------------------------------

index = pc.Index(
    PINECONE_INDEX_NAME
)


# --------------------------------------------------
# Store Chunks
# --------------------------------------------------

def store_chunks(
    video_id,
    chunks
):

    vectors = []

    print(
        "Pinecone index:",
        PINECONE_INDEX_NAME
    )

    print(
        "Total chunks:",
        len(chunks)
    )


    # --------------------------------------------------
    # Create Embeddings
    # --------------------------------------------------

    for number, chunk in enumerate(chunks):

        print(
            f"Creating embedding "
            f"{number + 1}/{len(chunks)}"
        )

        embedding = create_embedding(
            chunk["text"]
        )

        vectors.append({

            "id": chunk["id"],

            "values": embedding,

            "metadata": {

                "video_id": chunk["video_id"],

                "content_type": "video",

                "start_time": chunk["start_time"],

                "end_time": chunk["end_time"],

                "chunk": chunk["chunk"],

                "text": chunk["text"]
            }
        })


    # --------------------------------------------------
    # Upsert into Pinecone
    # --------------------------------------------------

    batch_size = 50

    total = 0


    for i in range(
        0,
        len(vectors),
        batch_size
    ):

        batch = vectors[
            i:i + batch_size
        ]

        print(
            f"Upserting batch "
            f"{i + 1} - "
            f"{i + len(batch)}"
        )

        try:

            index.upsert(
                vectors=batch,
                namespace=video_id
            )

            total += len(batch)

        except Exception as e:

            print(
                "PINECONE ERROR:",
                repr(e)
            )

            raise


    print(
        "Total vectors stored:",
        total
    )

    return total