import streamlit as st

# This will actually show up on the web page!
st.title("🎈 My First Streamlit App")

st.write("Hello, world! If you can see this, Streamlit is working perfectly.")

# An interactive widget just to test functionality
if st.button("Click Me"):
    st.success("It works! 🎉")

