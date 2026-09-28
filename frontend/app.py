import os
import json

import requests
import streamlit as st

from dotenv import load_dotenv


# ==================================================
# Configuration
# ==================================================

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

VIDEO_STORE_FILE = "processed_videos.json"


# ==================================================
# Helper Functions
# ==================================================

def format_time(seconds):

    seconds = int(seconds)

    hours = seconds // 3600

    minutes = (seconds % 3600) // 60

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


def load_processed_videos():

    if not os.path.exists(VIDEO_STORE_FILE):

        return []

    try:

        with open(
            VIDEO_STORE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):

                return data

            return []

    except Exception:

        return []


def save_processed_video(video):

    videos = load_processed_videos()

    # Remove duplicate video ID
    videos = [
        item
        for item in videos
        if item.get("video_id") != video.get("video_id")
    ]

    # Add newest video at top
    videos.insert(0, video)

    with open(
        VIDEO_STORE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            videos,
            file,
            indent=4
        )


def open_video(
    video_id,
    video_url,
    total_chunks=None
):

    st.session_state.video_id = video_id

    st.session_state.video_url = video_url

    st.session_state.total_chunks = total_chunks

    st.session_state.chat_history = []


# ==================================================
# Streamlit Configuration
# ==================================================

st.set_page_config(

    page_title="AI Video Assistant",

    page_icon="🎥",

    layout="wide"
)


# ==================================================
# Header
# ==================================================

st.title(
    "🎥 AI Video Assistant"
)

st.caption(
    "Process YouTube videos once and ask questions using AI."
)


# ==================================================
# Session State
# ==================================================

if "video_id" not in st.session_state:

    st.session_state.video_id = None


if "video_url" not in st.session_state:

    st.session_state.video_url = None


if "total_chunks" not in st.session_state:

    st.session_state.total_chunks = None


if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


# ==================================================
# Load processed videos
# ==================================================

processed_videos = load_processed_videos()


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header(
    "🎥 Video"
)


# ==================================================
# 1. PROCESS NEW VIDEO
# ==================================================

st.sidebar.subheader(
    "➕ Process New Video"
)


video_url = st.sidebar.text_input(

    "YouTube URL",

    placeholder=(
        "https://www.youtube.com/watch?v=..."
    ),

    key="new_video_url"
)


if st.sidebar.button(
    "🚀 Process Video",
    use_container_width=True
):

    if not video_url.strip():

        st.sidebar.error(
            "Please enter a YouTube URL."
        )

    else:

        with st.spinner(
            "Getting transcript and indexing..."
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/videos/process",

                    json={
                        "url": video_url.strip()
                    },

                    timeout=600
                )


                if response.status_code == 200:

                    data = response.json()


                    # ------------------------------
                    # Store current video
                    # ------------------------------

                    st.session_state.video_id = (
                        data["video_id"]
                    )

                    st.session_state.video_url = (
                        data["video_url"]
                    )

                    st.session_state.total_chunks = (
                        data["total_chunks"]
                    )

                    st.session_state.chat_history = []


                    # ------------------------------
                    # Save to local history
                    # ------------------------------

                    save_processed_video({

                        "video_id":
                            data["video_id"],

                        "video_url":
                            data["video_url"],

                        "total_chunks":
                            data["total_chunks"]

                    })


                    st.success(
                        "✅ Video processed successfully!"
                    )

                    st.rerun()


                else:

                    try:

                        error_message = (
                            response.json().get(
                                "detail",
                                response.text
                            )
                        )

                    except Exception:

                        error_message = response.text


                    st.sidebar.error(
                        error_message
                    )


            except requests.exceptions.RequestException as e:

                st.sidebar.error(
                    f"Could not connect to FastAPI: {e}"
                )


# ==================================================
# 2. OPEN EXISTING VIDEO
# ==================================================

st.sidebar.divider()

st.sidebar.subheader(
    "📂 Open Existing Video"
)


existing_video_id = st.sidebar.text_input(

    "Video ID",

    placeholder=(
        "Paste existing video ID"
    ),

    key="existing_video_id"
)


existing_video_url = st.sidebar.text_input(

    "YouTube URL",

    placeholder=(
        "https://www.youtube.com/watch?v=..."
    ),

    key="existing_video_url"
)


if st.sidebar.button(

    "📂 Open Video",

    use_container_width=True

):

    if not existing_video_id.strip():

        st.sidebar.error(
            "Please enter Video ID."
        )

    elif not existing_video_url.strip():

        st.sidebar.error(
            "Please enter YouTube URL."
        )

    else:

        # ------------------------------------------
        # Open without processing
        # ------------------------------------------

        open_video(

            existing_video_id.strip(),

            existing_video_url.strip(),

            None

        )


        # ------------------------------------------
        # Save into local history
        # ------------------------------------------

        save_processed_video({

            "video_id":
                existing_video_id.strip(),

            "video_url":
                existing_video_url.strip(),

            "total_chunks":
                None

        })


        st.rerun()


# ==================================================
# 3. SEARCH PROCESSED VIDEOS
# ==================================================

st.sidebar.divider()

st.sidebar.subheader(
    "🔎 Search Processed Videos"
)


search_text = st.sidebar.text_input(

    "Search",

    placeholder=(
        "Search URL or video ID..."
    ),

    key="search_videos"
)


filtered_videos = processed_videos


if search_text.strip():

    search_value = search_text.lower().strip()


    filtered_videos = [

        video

        for video in processed_videos

        if (
            search_value
            in video.get(
                "video_url",
                ""
            ).lower()
        )

        or (

            search_value
            in video.get(
                "video_id",
                ""
            ).lower()

        )

    ]


# --------------------------------------------------
# Existing video list
# --------------------------------------------------

if filtered_videos:

    video_labels = []

    video_lookup = {}


    for video in filtered_videos:

        video_id = video.get(
            "video_id",
            ""
        )

        video_url_item = video.get(
            "video_url",
            ""
        )


        label = (
            f"{video_url_item} "
            f" | ID: {video_id}"
        )


        video_labels.append(
            label
        )


        video_lookup[label] = video


    selected_label = st.sidebar.selectbox(

        "Select video",

        video_labels,

        key="selected_processed_video"
    )


    selected_video = video_lookup[
        selected_label
    ]


    if st.sidebar.button(

        "📂 Open Selected Video",

        use_container_width=True

    ):

        open_video(

            selected_video["video_id"],

            selected_video["video_url"],

            selected_video.get(
                "total_chunks"
            )

        )

        st.rerun()


else:

    st.sidebar.caption(
        "No processed videos found."
    )


# ==================================================
# CURRENT VIDEO STATUS
# ==================================================

if st.session_state.video_id:

    st.sidebar.divider()

    st.sidebar.success(
        "✅ Video Ready"
    )


    st.sidebar.write(
        f"Video ID: "
        f"{st.session_state.video_id}"
    )


    if st.session_state.total_chunks:

        st.sidebar.write(
            f"Chunks: "
            f"{st.session_state.total_chunks}"
        )


# ==================================================
# MAIN UI
# ==================================================

if not st.session_state.video_id:

    st.info(
        "👈 Process a new YouTube video "
        "or open an existing video."
    )


else:

    # ==================================================
    # VIDEO
    # ==================================================

    st.subheader(
        "🎥 Video"
    )


    st.video(
        st.session_state.video_url
    )


    st.divider()


    # ==================================================
    # CHAT
    # ==================================================

    st.subheader(
        "💬 Ask Your Video"
    )


    # ==================================================
    # CHAT HISTORY
    # ==================================================

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


            if (

                message["role"] == "assistant"

                and message.get("timestamps")

            ):

                timestamp_text = []


                for timestamp in message[
                    "timestamps"
                ]:

                    timestamp_text.append(

                        f"{format_time(timestamp['start'])}"
                        f" - "
                        f"{format_time(timestamp['end'])}"

                    )


                st.caption(

                    "🎥 Retrieved timestamps: "

                    + ", ".join(
                        timestamp_text
                    )

                )


    # ==================================================
    # ASK QUESTION
    # ==================================================

    question = st.chat_input(

        "Ask something about this video..."
    )


    if question:

        # ----------------------------------------------
        # User message
        # ----------------------------------------------

        st.session_state.chat_history.append({

            "role": "user",

            "content": question

        })


        with st.chat_message("user"):

            st.markdown(
                question
            )


        # ----------------------------------------------
        # Assistant
        # ----------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching transcript..."
            ):

                try:

                    response = requests.post(

                        f"{BACKEND_URL}/videos/"
                        f"{st.session_state.video_id}/ask",

                        json={
                            "question": question
                        },

                        timeout=180
                    )


                    if response.status_code == 200:

                        data = response.json()


                        answer = data.get(

                            "answer",

                            "No answer returned."

                        )


                        timestamps = data.get(

                            "timestamps",

                            []

                        )


                        # --------------------------
                        # Answer
                        # --------------------------

                        st.markdown(
                            answer
                        )


                        # --------------------------
                        # Timestamps
                        # --------------------------

                        if timestamps:

                            timestamp_text = []


                            for timestamp in timestamps:

                                timestamp_text.append(

                                    f"{format_time(timestamp['start'])}"
                                    f" - "
                                    f"{format_time(timestamp['end'])}"

                                )


                            st.caption(

                                "🎥 Retrieved timestamps: "

                                + ", ".join(
                                    timestamp_text
                                )

                            )


                        # --------------------------
                        # Save chat history
                        # --------------------------

                        st.session_state.chat_history.append({

                            "role": "assistant",

                            "content": answer,

                            "timestamps": timestamps

                        })


                    else:

                        try:

                            error_message = (
                                response.json().get(
                                    "detail",
                                    response.text
                                )
                            )

                        except Exception:

                            error_message = (
                                response.text
                            )


                        st.error(
                            error_message
                        )


                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Could not connect to FastAPI: {e}"
                    )