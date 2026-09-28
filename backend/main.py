from fastapi import FastAPI

from backend.routes.videos import (
    router as video_router
)


app = FastAPI(
    title="AI Video Assistant"
)


app.include_router(
    video_router
)


@app.get("/")
def root():

    return {

        "message": (
            "AI Video Assistant API"
        )
    }