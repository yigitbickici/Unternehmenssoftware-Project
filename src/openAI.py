import chainlit as cl
import requests
from openai import OpenAI
from openai.types.beta.threads import MessageContentText

api_key = ""
client = OpenAI(api_key=api_key)


assistant_id = "asst_wlsvbnbpvO04JnnYp5AkF0q0"


def create_thread():
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        'OpenAI-Beta': "assistants=v1"
    }

    url = "https://api.openai.com/v1/threads"

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        thread_id = response.json().get('id')
        return thread_id
    else:
        print("an error occured while creating thread:", response.text)
        return None

@cl.on_chat_start
def on_chat_start():
    thread_id = create_thread()
    cl.user_session.set("thread_id", thread_id)

@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message.content
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Please address the user as Emircan Capkan. The user has a premium account."
    )

    finished = False
    while not finished:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run.status != "in_progress":
            finished = True

    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )

    print(messages)
    assistant_response = []
    for message in messages:
        if message.content and isinstance(message.content[0], MessageContentText):
            value = message.content[0].text.value
            assistant_response.append(value)
            assistant_response.append(message.thread_id)

    await cl.Message(content=assistant_response[0]).send()
    await cl.Message(content=f"thread_id: {assistant_response[1]}").send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit("app.py")
