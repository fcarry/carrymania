from diffusers import StableDiffusionPipeline
import torch
import streamlit as st

# Streamlit app title
st.title("Generate Image with Stable Diffusion")

# User input for the prompt
prompt = st.text_input("Enter a description for the image:")

# Button to generate the image
if st.button("Generate Image"):
    if prompt:
        # Load the Stable Diffusion pipeline
        with st.spinner("Loading model..."):
            model_id = "CompVis/stable-diffusion-v1-4"
            pipe = StableDiffusionPipeline.from_pretrained(model_id)
            pipe = pipe.to("cpu")  # Usa GPU si está disponible

        # Generate the image
        with st.spinner("Generating image..."):
            image = pipe(prompt).images[0]

        # Display the generated image
        st.image(image, caption=f"Generated Image: {prompt}", use_container_width=True)
    else:
        st.warning("Please enter a description for the image.")

