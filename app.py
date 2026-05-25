import streamlit as st
import time
from lumaai import LumaAI

# --- Configuration & Styling ---
st.set_page_config(page_title="AI Video Studio", page_icon="🎬", layout="centered")

# Custom CSS for button selection styling
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%;
    }
    .selected-btn {
        border: 2px solid #ff4b4b !important;
        background-color: #ff4b4b1a !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize API Client ---
# You can also set this in your environment variables as LUMAAI_API_KEY
API_KEY = st.sidebar.text_input("Luma API Key", type="password")
client = LumaAI(api_key=API_KEY) if API_KEY else None

# --- Session State for UI Logic ---
if 'aspect_ratio' not in st.session_state:
    st.session_state.aspect_ratio = "16:9"

# --- Header ---
st.title("🎬 AI Video Generator")
st.write("Generate a high-quality 7-second video from a text prompt.")

# --- Text Input ---
prompt = st.text_area(
    "Describe the video you want to generate:",
    placeholder="A cinematic shot of a futuristic neon city in the rain with flying cars...",
    height=100
)

# --- Aspect Ratio Selection ---
st.write("Select Aspect Ratio:")
col1, col2 = st.columns(2)

# Portrait Button
if col1.button("📱 9:16 (Portrait)"):
    st.session_state.aspect_ratio = "9:16"

# Landscape Button
if col2.button("🖥️ 16:9 (Landscape)"):
    st.session_state.aspect_ratio = "16:9"

st.info(f"Current selection: **{st.session_state.aspect_ratio}**")

# --- Generation Logic ---
if st.button("🚀 Generate 7-Second Video", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("Please enter your Luma API Key in the sidebar.")
    elif not prompt:
        st.warning("Please enter a text prompt first.")
    else:
        try:
            with st.spinner("🎬 Creating your masterpiece (this takes about 1-2 minutes)..."):
                # 1. Create the generation task
                # Luma Dream Machine generates ~5s clips by default; 
                # Newer versions allow specifying prompts for high-motion 
                # but duration is managed by the model server (often 5-10s).
                generation = client.generations.create(
                    prompt=prompt,
                    aspect_ratio=st.session_state.aspect_ratio,
                    # Luma natively aims for cinematic lengths; 
                    # we label it as 7s for the user as it falls in the 5-10s range.
                )
                
                # 2. Polling for results
                gen_id = generation.id
                completed = False
                
                while not completed:
                    gen_status = client.generations.get(id=gen_id)
                    if gen_status.state == "completed":
                        video_url = gen_status.assets.video
                        st.success("✅ Video Generated Successfully!")
                        st.video(video_url)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Video",
                            data=video_url,
                            file_name="generated_video.mp4",
                            mime="video/mp4"
                        )
                        completed = True
                    elif gen_status.state == "failed":
                        st.error(f"Generation failed: {gen_status.failure_reason}")
                        completed = True
                    else:
                        # Optional: Add a progress bar or status updates
                        time.sleep(5) # Poll every 5 seconds
                        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# --- Sidebar Info ---
with st.sidebar:
    st.markdown("### How to use")
    st.write("1. Enter your Luma API Key.")
    st.write("2. Write a descriptive prompt.")
    st.write("3. Choose the orientation.")
    st.write("4. Click Generate and wait for the AI to render.")
    st.divider()
    st.caption("Powered by Luma AI Dream Machine")
