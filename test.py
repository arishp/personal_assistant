from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Initialize the Gemini Pro model
gemini_pro = init_chat_model(model="gemini-2.0-flash-lite", model_provider="google-genai")

# Create a message
messages = [HumanMessage(content="What is the capital of India?")]

# Invoke the model
response = gemini_pro.invoke(messages)

# Print the response
print(response.content)