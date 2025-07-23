import streamlit as st
import requests
import tempfile
import subprocess
import os
import json
import time
from pathlib import Path

# Configuration
LOCALAI_BASE_URL = "http://localhost:8080"
WHISPER_MODEL = "whisper-base"

# Color palette (following existing project style)
primary_color = "#1E90FF"
secondary_color = "#FF6347"
background_color = "#F5F5F5"
text_color = "#4561e9"

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {background_color};
        color: {text_color};
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }}
    .stFileUploader>div>div>div>button {{
        background-color: {secondary_color};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }}
    .subtitle-overlay {{
        position: relative;
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        text-align: center;
        font-size: 16px;
    }}
    </style>
""", unsafe_allow_html=True)

def check_localai_health():
    """Check if LocalAI is running and healthy"""
    try:
        response = requests.get(f"{LOCALAI_BASE_URL}/v1/models", timeout=5)
        return response.status_code == 200
    except:
        return False

def transcribe_audio_with_localai(audio_path):
    """Transcribe audio using LocalAI whisper-base model"""
    try:
        with open(audio_path, 'rb') as audio_file:
            files = {'file': audio_file}
            data = {'model': WHISPER_MODEL}
            
            response = requests.post(
                f"{LOCALAI_BASE_URL}/v1/audio/transcriptions",
                files=files,
                data=data,
                timeout=300  # 5 minute timeout for transcription
            )
            
        if response.status_code == 200:
            result = response.json()
            return result.get('text', '')
        else:
            st.error(f"Error transcribing audio: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to LocalAI: {str(e)}")
        return None

def extract_audio_from_video(video_path, audio_path):
    """Extract audio from video using ffmpeg"""
    try:
        cmd = [
            "ffmpeg", "-i", video_path, 
            "-vn", "-acodec", "pcm_s16le", 
            "-ar", "16000", "-ac", "1", 
            audio_path, "-y"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        st.error(f"Error extracting audio: {str(e)}")
        return False

def create_srt_subtitles(text, duration_seconds=None):
    """Create simple SRT format subtitles from transcribed text"""
    if not text:
        return ""
    
    # Simple subtitle creation - split text into chunks and estimate timing
    words = text.split()
    words_per_subtitle = 8  # Approximately 8 words per subtitle
    subtitle_duration = 3  # 3 seconds per subtitle
    
    srt_content = ""
    subtitle_number = 1
    
    for i in range(0, len(words), words_per_subtitle):
        chunk = " ".join(words[i:i + words_per_subtitle])
        start_time = (subtitle_number - 1) * subtitle_duration
        end_time = start_time + subtitle_duration
        
        # Format time as SRT timestamp (HH:MM:SS,mmm)
        def seconds_to_srt_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millisecs = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
        
        start_srt = seconds_to_srt_time(start_time)
        end_srt = seconds_to_srt_time(end_time)
        
        srt_content += f"{subtitle_number}\n{start_srt} --> {end_srt}\n{chunk}\n\n"
        subtitle_number += 1
    
    return srt_content

# Streamlit app
st.title("🎬 Video Transcription with Subtitles")
st.markdown("Upload a video to extract audio, transcribe it using LocalAI Whisper-base, and view with subtitles")

# Check LocalAI health
if not check_localai_health():
    st.warning("⚠️ LocalAI is not ready yet. Please wait a moment and refresh the page.")
    if st.button("Check LocalAI Status"):
        if check_localai_health():
            st.success("✅ LocalAI is now ready!")
            st.rerun()
        else:
            st.error("❌ LocalAI is still not responding. Please check the Docker container logs.")
else:
    st.success("✅ LocalAI is ready!")

# File uploader
uploaded_video = st.file_uploader(
    "Upload a video file", 
    type=["mp4", "avi", "mov", "mkv", "webm"],
    help="Supported formats: MP4, AVI, MOV, MKV, WebM"
)

if uploaded_video is not None:
    # Display video information
    st.write(f"**File:** {uploaded_video.name}")
    st.write(f"**Size:** {uploaded_video.size / (1024*1024):.2f} MB")
    
    # Show video player
    st.video(uploaded_video)
    
    # Process button
    if st.button("🎯 Extract Audio and Generate Subtitles"):
        if not check_localai_health():
            st.error("LocalAI is not available. Please ensure the service is running.")
        else:
            with st.spinner("Processing video..."):
                # Create temporary files
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                    temp_video.write(uploaded_video.read())
                    video_path = temp_video.name
                
                audio_path = video_path.replace(".mp4", ".wav")
                
                try:
                    # Step 1: Extract audio
                    with st.spinner("🎵 Extracting audio from video..."):
                        if extract_audio_from_video(video_path, audio_path):
                            st.success("Audio extracted successfully!")
                        else:
                            st.error("Failed to extract audio from video.")
                            st.stop()
                    
                    # Step 2: Transcribe audio
                    with st.spinner("🎤 Transcribing audio with LocalAI Whisper-base..."):
                        transcribed_text = transcribe_audio_with_localai(audio_path)
                        
                        if transcribed_text:
                            st.success("Transcription completed!")
                            
                            # Display transcribed text
                            st.subheader("📝 Transcribed Text:")
                            st.text_area("Full Transcription:", transcribed_text, height=200)
                            
                            # Generate subtitles
                            st.subheader("📺 Subtitles (SRT Format):")
                            srt_content = create_srt_subtitles(transcribed_text)
                            st.text_area("SRT Subtitles:", srt_content, height=300)
                            
                            # Download options
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.download_button(
                                    label="📥 Download Transcription",
                                    data=transcribed_text,
                                    file_name=f"{uploaded_video.name}_transcription.txt",
                                    mime="text/plain"
                                )
                            
                            with col2:
                                st.download_button(
                                    label="📥 Download Subtitles (SRT)",
                                    data=srt_content,
                                    file_name=f"{uploaded_video.name}_subtitles.srt",
                                    mime="text/plain"
                                )
                            
                            # Display subtitle preview with video
                            st.subheader("🎬 Video with Subtitle Preview:")
                            st.markdown("""
                            **Note:** For full subtitle integration, download the SRT file and use it with your preferred video player.
                            Below is a preview of how the subtitles would appear:
                            """)
                            
                            # Simple subtitle preview
                            st.markdown(f"""
                            <div class="subtitle-overlay">
                            {transcribed_text[:200]}{'...' if len(transcribed_text) > 200 else ''}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        else:
                            st.error("Failed to transcribe audio. Please check LocalAI logs.")
                
                finally:
                    # Cleanup temporary files
                    try:
                        os.unlink(video_path)
                        if os.path.exists(audio_path):
                            os.unlink(audio_path)
                    except:
                        pass

# Information section
st.markdown("---")
st.markdown("""
### ℹ️ How it works:
1. **Upload Video**: Choose any supported video format
2. **Audio Extraction**: FFmpeg extracts audio from the video
3. **Speech Recognition**: LocalAI with Whisper-base model transcribes the audio
4. **Subtitle Generation**: Creates SRT format subtitles with timing
5. **Download**: Get both transcription text and SRT subtitle files

### 🔧 Technology Stack:
- **LocalAI**: Self-hosted AI API
- **Whisper-base**: OpenAI's speech recognition model
- **Streamlit**: Web interface
- **FFmpeg**: Audio/video processing
- **Docker**: Containerized deployment
""")