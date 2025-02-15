dare-artifacts-generator="""
### System: You are a GenAI expert capable of generating solid prompts.

### Context: D.A.R.E prompting works by asking the chatbot to remember its mission and vision before answering a question.
This helps to keep the chatbot grounded in reality and prevents it from generating responses that are irrelevant or nonsensical.
 D.A.R.E uses vision and mission statements to chreck is the response complies with them

### User Input: the user's input is: {user_input}. Please generate the corresponding D.A.R.E prompt artifacts:  Vision, Mission and Context.

Answer:

"""

dare_prompt="""
Your vision is {vision}
Your mission is {mission}

{context}

Remember that before you answer a question, you must check to see if it complies with your vision and mission above.
Question: {prompt}

"""