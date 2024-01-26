import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
reponse = chat.send_message([
  'who is Odin?',
  # img,
], stream = True)

for chunk in response:
  print(chunk.text, end='')