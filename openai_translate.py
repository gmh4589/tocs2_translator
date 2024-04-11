from openai import OpenAI

client = OpenAI(api_key='')
client.base_url = 'http://127.0.0.1:1337'
client.models = 'ChatGPT-3.5-Turbo-16k-0613'

stream = client.chat.completions.create(
    model="gpt-3.5",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
