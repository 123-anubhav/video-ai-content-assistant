from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(video_url):

    if "youtu.be/" in video_url:

        return video_url.split(
            "youtu.be/"
        )[1].split("?")[0]

    if "youtube.com/watch" in video_url:

        return video_url.split(
            "v="
        )[1].split("&")[0]

    if "youtube.com/shorts/" in video_url:

        return video_url.split(
            "youtube.com/shorts/"
        )[1].split("?")[0]

    raise ValueError(
        "Unsupported YouTube URL"
    )


def get_transcript(video_url):

    video_id = extract_video_id(
        video_url
    )

    print(
        "Transcript video ID:",
        video_id
    )

    try:

        api = YouTubeTranscriptApi()

        transcript = api.fetch(
            video_id
        )

        print(
            "Transcript fetched:",
            len(transcript)
        )

        return [
            {
                "text": item.text,
                "start": item.start,
                "duration": item.duration
            }
            for item in transcript
        ]

    except Exception as e:

        print(
            "Transcript ERROR:",
            repr(e)
        )

        raise ValueError(
            f"Transcript not available: {str(e)}"
        )