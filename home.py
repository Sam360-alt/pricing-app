import streamlit as st

st.set_page_config(page_title="My App", layout="wide")
cl1,_, cl2 = st.columns([6,1,1])
with cl1:

    st.title("Welcome")
with cl2:
    if st.button("About me"):
        st.session_state["previous_page"] = "home.py"
        st.switch_page("pages/2_About.py")

st.markdown("""
### In this pricing application, you are positioned as a trader holding short positions in various options and structured products. Consequently, all analyses and risk metrics are presented from this perspective (for example, the Delta of a vanilla call option will appear negative)

Use the button below to navigate:
""")

# Create two columns for buttons

if st.button("📈 Go to Pricer"):
    st.switch_page("pages/1_Pricer.py")
