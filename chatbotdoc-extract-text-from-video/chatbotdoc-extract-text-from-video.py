import streamlit as st
import whisper
import tempfile
import subprocess

# Streamlit app title
st.title("Extract Text from Video")

# File uploader for video
uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

# Button to process the video and extract text
if st.button("Extract Text"):
    if uploaded_video:
        # Save the uploaded video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(uploaded_video.read())
            video_path = temp_video.name

        # Extract audio from the video using ffmpeg
        with st.spinner("Extracting audio from video..."):
            audio_path = video_path.replace(".mp4", ".wav")
            subprocess.run(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path])

        # Load Whisper model
        with st.spinner("Loading Whisper model..."):
            model = whisper.load_model("base")

        # Transcribe the audio to text
        with st.spinner("Transcribing audio..."):
            result = model.transcribe(audio_path)
            st.success("Transcription completed!")
            st.text_area("Extracted Text:", result["text"], height=300)

        # Clean up temporary files
        subprocess.run(["rm", video_path, audio_path])
    else:
        st.warning("Please upload a video file.")