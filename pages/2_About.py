import streamlit as st
from pathlib import Path

if st.button("←"):
    previous = st.session_state.get("previous_page", "home.py")
    st.switch_page(previous)


st.title("👤 About Me")

st.write("""
My name is Samuel Bokobza and I'm currently a Master's 1 student at Edhec following the Finance track. I have a strong interest in Financial Engineering and wanted to implement my knowledge from school and personal reasearch in a concrete project.
I have been learning python since end 2025 and this app is a summary of my skills so far. The Class GBM used to price options and structured products is code by hand. Otherwise, the streamlit website is coded with the help of an AI. 
Coding this app helped me learn a lot on the streamlit library and enhance my skills on object-oriented programming.
The knowledge on options and structured products used for this pricer comes from the book *Exotic Options and Hybrids, A guide to Structuring, Pricing and Trading* by Mohamed Bouzoubaa and Adel Osseiran.

I am currently looking for an internship in Trading or Structuring starting from june 2026.

Feel free to connect:

email: samuel.bokobza@edhec.com

linkedin: https://www.linkedin.com/in/samuel-bokobza-8249772b7/

GitHub: https://github.com/Sam360-alt
         """)

resume_path = Path("Bokobza_Samuel.pdf")

if resume_path.exists():
    with open(resume_path, "rb") as file:
        st.download_button(
            label="Download my resume",
            data=file,
            file_name="Bokobza_Samuel.pdf",
            mime="application/pdf"
        )
else:
    st.warning("Resume file not found.")