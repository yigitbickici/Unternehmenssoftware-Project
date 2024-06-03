import chainlit as cl
import requests

@cl.on_chat_start
def on_chat_start():
    cl.user_session.set("hist", "")

@cl.on_message
async def on_message(message: cl.Message):
    hist = cl.user_session.get("hist")

    params = {
        "message": hist + message.content,
    }

    url = 'http://localhost:4000/generate-response'

    x = requests.post(url, json=params)

    response_json = x.json()
    response_text = response_json["response"]

    cl.user_session.set("hist", hist + ' ' + response_text)

    await cl.Message(content=response_text).send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    import os
    script_path = os.path.abspath('/Users/yigitbickici/Documents/GitHub/Unternehmenssoftware-Project/src/app.py')
    run_chainlit(script_path)
