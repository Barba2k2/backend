import io
import json
import asyncio
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
        try:
            message = await websocket.receive_text()

            # Processar a mensagem recebida aqui
            # Supondo que message seja um JSON com uma chave 'text'
            data = json.loads(message)
            user_message = data['text']

            # Enviar a mensagem para a API de chat e aguardar a resposta
            response = chat.send_message([user_message], stream=True)

            # Enviar a resposta de volta ao WebSocket
            for chunk in response:
                await websocket.send_text(chunk.text)

        except json.JSONDecodeError:
            # Tratar o erro de decodificação JSON
            await websocket.send_text("Erro de formato de mensagem.")
        except asyncio.CancelledError:
            # Tratar a desconexão do WebSocket
            break
        except Exception as e:
            # Tratar outros erros
            await websocket.send_text(f"Erro no servidor: {str(e)}")

    await websocket.close()

@app.get('/fetch-messages', response_model=List[dict])
async def fetch_messages():
  return [{'role': message.role, 'text': message.parts[0].text} for message in chat.history]

if __name__ == '__main__':
  import uvicorn

  uvicorn.run(app, host='127.0.0.1', port=8000)