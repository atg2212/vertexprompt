import os
import streamlit as st
from initialization import initialize_llm_vertex
# from vertexai.preview.vision_models import Image, ImageGenerationModel
from gptrim import trim
from prompts import *
from prompts import SYSTEM_PROMPT
from placeholders import *
from system_prompts import *
import requests
from meta_prompt import *
from google.genai import types
from fine_tune_prompt import *
from agent_prompt import *
from google.genai.types import (GenerateContentConfig,)

# https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config
st.set_page_config(
    page_title="The Prompt Playground",
    page_icon="icons/vertexai.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': 'https://github.com/UriKatsirPrivate/prompt-playground',
        'About': "#### Created by [Uri Katsir](https://www.linkedin.com/in/uri-katsir/)"
    }
)

# REGIONS=["europe-west4","us-central1","us-west4","us-west1"]
REGIONS=["us-central1"]
MODEL_NAMES=['gemini-2.0-flash-001','gemini-2.0-flash-lite-preview-02-05','gemini-2.0-pro-exp-02-05','gemini-1.5-pro-002','gemini-1.5-flash-002']

def get_project_id():
    return "landing-zone-demo-341118"

project_id=get_project_id()
st.sidebar.write("Project ID: ",f"{project_id}") 
region=st.sidebar.selectbox("Region",REGIONS)
model_name = st.sidebar.selectbox('Model Name',MODEL_NAMES)
max_tokens = st.sidebar.slider('Output Token Limit',min_value=1,max_value=8192,step=100,value=8192)
temperature = st.sidebar.slider('Temperature',min_value=0.0,max_value=2.0,step=0.1,value=1.0)
top_p = st.sidebar.slider('Top-P',min_value=0.0,max_value=1.0,step=0.1,value=0.8)

css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1.15rem;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6= st.tabs(["Fine-Tune Prompt / ",
                                             "Run Prompt / ",
                                             "Agent Prompt / ",
                                             "Meta Prompt / ",
                                             "Zero to Few / ",
                                             "Chain of Thought / "])

client, safety_settings,generation_config = initialize_llm_vertex(project_id,region,model_name,max_tokens,temperature,top_p)

with tab1:
    
    def fine_tune_prompt(user_input):
        
        prompt= supercharge_prompt
        
        goal="improve the prompt"
        
        formatted_prompt = prompt.format(goal=goal,prompt=user_input)

        response = client.models.generate_content(
            model=model_name,
            contents=formatted_prompt,
            config=generation_config,
            )
        return(response.text)
    
    def display_result(execution_result):
        if execution_result != "":
            st.text_area(label="Execution Result:",value=execution_result,height=400, key=50)
        else:
            st.warning('No result to display.')    

    with st.form(key='fine-tune',clear_on_submit=False):
    #Get the prompt from the user
        prompt = st.text_area('Enter your prompt:',height=200, key=33,placeholder="tweet about Israel")
        
        if st.form_submit_button('Fine-Tune Prompt',disabled=not (project_id)  or project_id=="Your Project ID"):
            if prompt:
                with st.spinner('Generating prompts...'):
                    execution_result = fine_tune_prompt(prompt)
                display_result(execution_result)
            else:
                st.warning('Please enter a prompt before executing.')
with tab2:
    
    def run_prompt(prompt):
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text 


    def display_result(execution_result):
        if execution_result != "":
            st.text_area(label="Execution Result:",value=execution_result,height=400, key=50)
        else:
            st.warning('No result to display.')    

    with st.form(key='run-prompt',clear_on_submit=False):
    #Get the prompt from the user
        prompt = st.text_area('Enter your prompt:',height=200, key=1,placeholder="")
        
        if st.form_submit_button('Run Prompt',disabled=not (project_id)  or project_id=="Your Project ID"):
            if prompt:
                with st.spinner('Running prompt...'):
                    execution_result = run_prompt(prompt)
                display_result(execution_result)
            else:
                st.warning('Please enter a prompt before executing.')                
with tab3:
    
    def create_agent_prompt(user_input):
        
        prompt= agent_prompt
        
        # goal="improve the prompt"
        
        formatted_prompt = prompt.format(prompt=user_input)

        response = client.models.generate_content(
            model=model_name,
            contents=formatted_prompt,
            config=generation_config,
            )
        return(response.text)
    
    def display_result(execution_result):
        if execution_result != "":
            st.text_area(label="Execution Result:",value=execution_result,height=400, key=50)
        else:
            st.warning('No result to display.')    

    with st.form(key='agent-prompt',clear_on_submit=False):
    #Get the prompt from the user
        prompt = st.text_area('Enter your prompt:',height=200, key=3,placeholder="")
        
        if st.form_submit_button('Agent Prompt',disabled=not (project_id)  or project_id=="Your Project ID"):
            if prompt:
                with st.spinner('Generating agent prompt...'):
                    execution_result = create_agent_prompt(prompt)
                display_result(execution_result)
            else:
                st.warning('Please enter a prompt before executing.')
with tab4:
    def create_meta_prompt(user_input):
        response = client.models.generate_content(
            model=model_name,
            contents=user_input,
            config=generation_config,
            )
        return(response.text)
    
    def display_result(execution_result):
        if execution_result != "":
            st.text_area(label="Execution Result:",value=execution_result,height=400, key=50)
        else:
            st.warning('No result to display.')    

    with st.form(key='metaprompt',clear_on_submit=False):
    #Get the prompt from the user
        prompt = st.text_area('Enter your prompt:',height=200, key=4,placeholder="")
        
        if st.form_submit_button('Meta-Prompt',disabled=not (project_id)  or project_id=="Your Project ID"):
            if prompt:
                TASK=prompt
                with st.spinner('Generating meta-prompt...'):
                    prompt = metaprompt.replace("{{TASK}}", TASK)
                    assistant_partial = "<Inputs>"
                    execution_result = create_meta_prompt(prompt)
                display_result(execution_result)
            else:
                st.warning('Please enter a prompt before executing.')     
with tab5:
    
    def zero_to_few_prompt(user_input):
        system_prompt ="""
                        You are an assistant designed to convert a zero-shot prompt into a few-shot prompt.
        """


        prompt= """The zero-shot prompt is: '{zero_shot_prompt}'. Please convert it into a few-shot prompt.
                   Be as elaborate as possible. Make sure to include at least 3 examples.
                """
        
        formatted_prompt = prompt.format(zero_shot_prompt=user_input)

        generation_config = GenerateContentConfig(temperature=temperature,
                                          top_p=top_p,
                                          max_output_tokens=max_tokens,
                                          system_instruction=system_prompt,
                                          response_modalities = ["TEXT"],
                                          safety_settings=safety_settings,
                                    )

        response = client.models.generate_content(
            model=model_name,
            contents=formatted_prompt,
            config=generation_config,
            )
        return(response.text)
    
    def display_result(execution_result):
        if execution_result != "":
            st.text_area(label="Execution Result:",value=execution_result,height=400, key=50)
        else:
            st.warning('No result to display.')    

    with st.form(key='zero-to-few',clear_on_submit=False):
    #Get the prompt from the user
        prompt = st.text_area('Enter your prompt:',height=200, key=5,placeholder="")
        
        if st.form_submit_button('Zero to few',disabled=not (project_id)  or project_id=="Your Project ID"):
            if prompt:
                with st.spinner('Generating prompt with shots...'):
                    execution_result = zero_to_few_prompt(prompt)
                display_result(execution_result)
            else:
                st.warning('Please enter a prompt before executing.')
with tab6:
    
    def chain_of_thought_prompt(user_input):
        system_prompt ="""
                        You are an assistant designed to convert a prompt into a chain of thought prompt.
        """


        prompt= """The prompt is: '{prompt}'. Please convert it into a chain of thought prompt.
                    Always append 'Let's think step by step.' to the prompt.
                """
        
        formatted_prompt = prompt.format(prompt=user_input)

        generation_config = GenerateContentConfig(temperature=temperature,
                                          top_p=top_p,
                                          max_output_tokens=max_tokens,
                                          system_instruction=system_prompt,
                                          response_modalities = ["TEXT"],
                                          safety_settings=safety_settings,
                                    )

        response = client.models.generate_content(
            model=model_name,
            contents=formatted_prompt,
            config=generation_config,
            )
        return(response.text)
    
    def display_result(execution_result):
        if execution_result != "":
            st.text_area(label="Execution Result:",value=execution_result,height=400, key=50)
        else:
            st.warning('No result to display.')    

    with st.form(key='chain-of-thought',clear_on_submit=False):
    #Get the prompt from the user
        prompt = st.text_area('Enter your prompt:',height=200, key=6,placeholder="")
        
        if st.form_submit_button('Chain of thought',disabled=not (project_id)  or project_id=="Your Project ID"):
            if prompt:
                with st.spinner('Generating Chain of thought prompt...'):
                    execution_result = chain_of_thought_prompt(prompt)
                display_result(execution_result)
            else:
                st.warning('Please enter a prompt before executing.')                                           