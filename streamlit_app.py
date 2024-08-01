import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express
import google.generativeai as genai
import re

GEMINI_KEY = st.secrets.GEMINI_API_KEY

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


def read_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

def extract_code_content(text):
    match = re.search(r"```python\n(.*)\n```", text, flags=re.DOT
    if match:
        return match.group(1)
    else:
        return None


# streamlit web app configuration
st.set_page_config(
    page_title="Data Chat",
    page_icon="📊",
    layout="centered",
)

# streamlit page title
st.title("🤖 Data Chat")
st.subheader("Powered by Google's Gemini✨")

# initialize chat history in streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# initiate df iin session state
if "df" not in st.session_state:
    st.session_state.df = None


# file upload widget
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    st.session_state.df = read_data(uploaded_file)
    st.write("DataFrame Preview:")
    st.dataframe(st.session_state.df,use_container_width=True)


# display chat history
for message in st.session_state.chat_history:
    if message["content"] != 'st.error("Prompt is not specific/irrelevant")':
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                exec(message["content"])
            else:
                st.markdown(message["content"])




if uploaded_file:
    chat_input_disabled = False
else:
    chat_input_disabled = True


# input field for user's message
if chat_input_disabled:
    user_prompt = st.chat_input("Upload CSV/Excel file above...",disabled=chat_input_disabled)
else:
    user_prompt = st.chat_input("Enter your prompt",disabled=chat_input_disabled)




if user_prompt:
    # add user's message to chat history and display it
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role":"user","content": user_prompt})


    gemini_response = model.generate_content(f"""
Help me writing streamlit code.
I have imported these -
    import pandas as pd
    import numpy as np
    import streamlit as st
    import plotly
I have a dataframe st.session_state.df initialized with the data.
The Dataframe has columns - {st.session_state.df.columns}.
You will output only the streamlit python code snippet.
This code snippet will be executed in my streamlit app and appened to chat history.
DO NOT USE ANY OTHER LIBRARY
ONLY USE PLOTLY FUNCTIONS TO DISPLAY CHARTS AND GRAPHS / PLOTTING
The question is -
                        
{user_prompt}

if the text above is not a question please return "st.error("Prompt is not specific/irrelevant")"
    """).text

    code_to_execute =extract_code_content(gemini_response)
    # display LLM response
    if code_to_execute != 'st.error("Prompt is not specific/irrelevant")':
        with st.chat_message("⚙️"):
                st.markdown(gemini_response)
    
    
    block = 0
    while block < 3:
        with st.chat_message("assistant"):
                try:
                    exec(code_to_execute)
                    break
                except:
                    block += 1
    else:
        st.error("Unable to execute the code. Please try again.")
    
    if code_to_execute != 'st.error("Prompt is not specific/irrelevant")':
        st.session_state.chat_history.append({"role":"⚙️", "content": gemini_response})
        st.session_state.chat_history.append({"role":"assistant", "content": code_to_execute})
