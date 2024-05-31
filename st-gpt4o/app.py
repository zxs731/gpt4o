  
import requests
import streamlit as st
import json, ast
import openai
from dotenv import load_dotenv  
import os
from PIL import Image
import numpy as np
from io import BytesIO
from io import StringIO
import base64

load_dotenv("./gpt4o.env")  
os.environ["OPENAI_API_TYPE"] = os.environ["Azure_OPENAI_API_TYPE1"]
os.environ["OPENAI_API_BASE"] = os.environ["Azure_OPENAI_API_BASE1"]
os.environ["OPENAI_API_KEY"] =  os.environ["Azure_OPENAI_API_KEY1"]
os.environ["OPENAI_API_VERSION"] = os.environ["Azure_OPENAI_API_VERSION1"]
BASE_URL=os.environ["OPENAI_API_BASE"]
API_KEY=os.environ["OPENAI_API_KEY"]
CHAT_DEPLOYMENT_NAME=os.environ.get('Azure_OPENAI_Chat_API_Deployment_GPT4o')
openai.api_type = os.environ["OPENAI_API_TYPE"]
openai.api_base = os.environ["OPENAI_API_BASE"]
openai.api_version = os.environ["OPENAI_API_VERSION"]
openai.api_key = os.getenv("OPENAI_API_KEY")

def run_conversation(question):    
    system_message = {"role":"system","content":""}
    i=20
    messages = st.session_state.messages[-i:]
    while messages[0]=='assistant':
        i+=1
        messages = st.session_state.messages[-i:]
    ##print(messages)
    response = openai.ChatCompletion.create(
        engine=CHAT_DEPLOYMENT_NAME,
        messages = [system_message]+messages,
        temperature=0.6,
        max_tokens=1000,
        stream=True
    ) 
    
    for chunk in response:
        if chunk.choices:
            if 'content' in chunk.choices[0].delta:
                c=chunk.choices[0].delta.content
                if c is not None:
                    yield c


if "messages" not in st.session_state:
    st.session_state.messages = []

    
for message1 in st.session_state.messages:
    with st.chat_message(message1["role"]):
        #message1["content"][0]["text"]
        content=message1["content"][0]["text"]
        #content = content.replace('[', '$$').replace(']', '$$')  
        st.markdown(content)
        if len(message1["content"])>1 and "image_url" in message1["content"][1]:
            st.image(message1["content"][1]["image_url"]["url"],width=300)
        

uploaded_file = st.sidebar.file_uploader("Choose a picture",type=['png', 'jpg','jpeg','gif'] )
img_file_buffer = st.sidebar.camera_input("Take a picture")

if img_file_buffer is not None:
    bytes_data = img_file_buffer
    bytes_io = Image.open(img_file_buffer)
    encoded_image = base64.b64encode(bytes_data).decode('ascii')
    ##print(encoded_image)
    st.session_state.img =encoded_image
    st.sidebar.image(bytes_io,width=300)
if uploaded_file is not None:
    print("upload")
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    bytes_io = BytesIO(bytes_data)
    
    encoded_image = base64.b64encode(bytes_data).decode('ascii')
    #print(encoded_image)
    st.session_state.img =encoded_image# Image.open(bytes_io)
    st.sidebar.image(bytes_io,width=300)

if prompt := st.chat_input():
    st.chat_message("user").markdown(prompt)
    inputContent = [{
          "type": "text",
          "text": prompt
        }]
    if 'img' in st.session_state and st.session_state.img:
        inputContent=inputContent+[{
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{st.session_state.img}"
          }
        }]
    st.session_state.messages.append({"role": "user", "content": inputContent})
    with st.chat_message("assistant"):
        response = st.write_stream(run_conversation(prompt))
        content = [{
          "type": "text",
          "text": response
        }]
        st.session_state.messages.append({"role": "assistant", "content": content})    
        st.session_state.img=None
