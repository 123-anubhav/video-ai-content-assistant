import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.transcript_service import get_transcript
from backend.services.chunk_service import create_chunks
from backend.services.pinecone_service import store_chunks
from backend.services.rag_service import ask_video


router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)


class VideoRequest(BaseModel):
    url: str


class QuestionRequest(BaseModel):
    question: str


# --------------------------------------------------
# Process Video
# --------------------------------------------------

@router.post("/process")
def process_video(request: VideoRequest):

    video_id = str(uuid.uuid4())

    print("STEP 1: Video ID =", video_id)

    try:

        print("STEP 2: Getting transcript...")

        transcript = get_transcript(request.url)

        print(
            "STEP 3: Transcript count =",
            len(transcript)
        )

        if not transcript:
            raise ValueError(
                "Transcript is empty"
            )

        print(
            "STEP 4: Creating chunks..."
        )

        chunks = create_chunks(
            transcript,
            video_id
        )

        print(
            "STEP 5: Chunk count =",
            len(chunks)
        )

        print(
            "STEP 6: Storing in Pinecone..."
        )

        total_chunks = store_chunks(
            video_id,
            chunks
        )

        print(
            "STEP 7: Pinecone storage complete"
        )

        return {
            "video_id": video_id,
            "video_url": request.url,
            "total_chunks": total_chunks,
            "message": (
                "Video transcript "
                "processed successfully"
            )
        }

    except Exception as e:

        print(
            "ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# --------------------------------------------------
# Ask Video Question
# --------------------------------------------------

@router.post("/{video_id}/ask")
def ask_video_question(
    video_id: str,
    request: QuestionRequest
):

    try:

        return ask_video(
            video_id,
            request.question
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )