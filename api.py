import io
import json
import os
from typing import List
import PIL.Image
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
chat= model.start_chat(history=[])

app = FastAPI()

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()

  while True:
    message = await websocket.receive()

    if isinstance(message, bytes):
      data = json.loads(message.decode())
      message = data['text']
      img_bytes = bytes(data['bytes'])
      img = PIL.Image.open(io.BytesIO(img_bytes))
      respose = chat.send_message([message, img], stream=True)
    else:
      if message == '<FIN>!':
        await websocket.close()
        break

    response = chat.send_message([message], stream = True)
  
  for chunk in response:
    await websocket.send_text(chunk.text)
  await websocket.send_text('<FIN>')