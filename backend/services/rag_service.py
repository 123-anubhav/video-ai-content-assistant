from pinecone import Pinecone

from backend.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME
)

from backend.services.embedding_service import (
    create_embedding
)

from backend.services.llm_service import (
    generate_answer
)


pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(
    PINECONE_INDEX_NAME
)


def ask_video(
    video_id,
    question
):

    # ---------------------------------------------
    # 1. Create question embedding
    # ---------------------------------------------

    question_vector = create_embedding(
        question
    )

    # ---------------------------------------------
    # 2. Search Pinecone
    # ---------------------------------------------

    result = index.query(

        namespace=video_id,

        vector=question_vector,

        top_k=5,

        include_metadata=True
    )

    matches = result.get(
        "matches",
        []
    )

    # ---------------------------------------------
    # 3. No relevant information
    # ---------------------------------------------

    if not matches:

        return {
            "answer": (
                "I could not find relevant "
                "information in the video transcript."
            ),
            "timestamps": []
        }

    # ---------------------------------------------
    # 4. Build context
    # ---------------------------------------------

    context_parts = []

    timestamps = []

    for match in matches:

        metadata = match.get(
            "metadata",
            {}
        )

        text = metadata.get(
            "text",
            ""
        )

        start_time = metadata.get(
            "start_time"
        )

        end_time = metadata.get(
            "end_time"
        )

        if text:

            context_parts.append(
                f"[{format_time(start_time)} - "
                f"{format_time(end_time)}]\n"
                f"{text}"
            )

        if (
            start_time is not None
            and end_time is not None
        ):

            timestamps.append({
                "start": start_time,
                "end": end_time
            })

    context = "\n\n".join(
        context_parts
    )

    # ---------------------------------------------
    # 5. LLM prompt
    # ---------------------------------------------

    prompt = f"""
You are an AI video assistant.

Answer the user's question using ONLY
the provided video transcript context.

If the answer is not present in the
context, say:

"The information was not found
in the video transcript."

Do not invent information.

Mention relevant timestamps when useful.

VIDEO TRANSCRIPT CONTEXT:

{context}

USER QUESTION:

{question}
"""

    # ---------------------------------------------
    # 6. Generate answer
    # ---------------------------------------------

    answer = generate_answer(
        prompt
    )

    return {
        "answer": answer,
        "timestamps": timestamps
    }


def format_time(seconds):

    if seconds is None:

        return "00:00"

    seconds = int(seconds)

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    seconds = seconds % 60

    if hours > 0:

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

    return (
        f"{minutes:02d}:"
        f"{seconds:02d}"
    )