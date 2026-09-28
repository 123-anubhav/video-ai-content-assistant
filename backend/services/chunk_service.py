from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


def create_chunks(
    transcript,
    video_id
):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1000,

        chunk_overlap=150
    )

    chunks = []

    current_text = ""
    current_start = None
    current_end = None

    chunk_number = 0

    for item in transcript:

        text = item["text"]

        start = item["start"]

        end = (
            item["start"]
            + item["duration"]
        )

        if current_start is None:

            current_start = start

        current_text += " " + text

        current_end = end

        if len(current_text) >= 1000:

            split_texts = splitter.split_text(
                current_text
            )

            for split_text in split_texts:

                chunks.append({

                    "id": (
                        f"{video_id}-"
                        f"chunk-{chunk_number}"
                    ),

                    "video_id": video_id,

                    "start_time": current_start,

                    "end_time": current_end,

                    "chunk": chunk_number,

                    "text": split_text
                })

                chunk_number += 1

            current_text = ""

            current_start = None

    if current_text.strip():

        chunks.append({

            "id": (
                f"{video_id}-"
                f"chunk-{chunk_number}"
            ),

            "video_id": video_id,

            "start_time": current_start,

            "end_time": current_end,

            "chunk": chunk_number,

            "text": current_text.strip()
        })

    return chunks