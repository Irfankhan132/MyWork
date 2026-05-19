import streamlit as st
from components.upload import render_upload
from components.ChatUI import render_chat
from components.history_download import render_history_download

st.set_page_config(page_title="AI Medical Assistant", page_icon=":hospital:", layout="wide")
st.title("Medical Assistant :Chatbot:")


render_upload()
render_chat()
render_history_download()