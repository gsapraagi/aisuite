
import aisuite as ai


client = ai.Client(    {
                    
    "perplexity" : {"api_key":"pplx-"}

})

models = ["perplexity:llama-3.1-sonar-large-128k-online"]

messages = [
    {"role": "system", "content": "Respond in Pirate English."},
    {"role": "user", "content": "Tell me a joke."},
]

for model in models:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.75,
        max_tokens = 8000
    )
    print(response.choices[0].message.content)
