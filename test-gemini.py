from google import genai

client = genai.Client(api_key="AIzaSyDD4jNglkc6zzg1YGyVdlqF-8NbfMdAwJQ")

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)