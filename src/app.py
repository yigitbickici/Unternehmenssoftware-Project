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

    try:
        response = requests.post(url, json=params)
        response.raise_for_status()  # İsteğin başarılı olup olmadığını kontrol et
        response_json = response.json()  # Yanıtı JSON olarak işleyin

        # Yanıtın beklenen anahtarları içerip içermediğini kontrol edin
        if "response" in response_json:
            response_text = response_json["response"]
        else:
            raise ValueError("Yanıt beklenen 'response' anahtarını içermiyor.")

    except requests.exceptions.HTTPError as http_err:
        await cl.Message(content=f'HTTP error occurred: {http_err.response.text}').send()  # HTTP hatalarını kullanıcıya gösterin
    except requests.exceptions.JSONDecodeError as json_err:
        await cl.Message(content=f'JSON decoding error occurred: {json_err}').send()  # JSONDecodeError hatasını gösterin
    except requests.exceptions.RequestException as req_err:
        await cl.Message(content=f'Request error occurred: {req_err}').send()  # Diğer istek hatalarını gösterin
    except Exception as err:
        await cl.Message(content=f'Other error occurred: {err}').send()  # Diğer tüm hataları gösterin
    else:
        cl.user_session.set("hist", hist + ' ' + response_text)
        await cl.Message(content=response_text).send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    import os
    script_path = os.path.abspath('/Users/yigitbickici/Documents/GitHub/Unternehmenssoftware-Project/src/app.py')
    run_chainlit(script_path)
