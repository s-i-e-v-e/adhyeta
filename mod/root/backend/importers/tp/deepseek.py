# set up deep seek translation pipeline
from mod.config import env

TRANSLATION_PROMPT = """
Translate the entire xml document (except the element-tags) into SANSKRIT ONLY (not Marathi/Hindi or other languages written using the devanagari script).
Do not add any additional text or explanations.
Do not mess with the apostrophes, quotation marks and other punctuation. 
""".strip()
def translate(sxml: str) -> str:
	from openai import OpenAI
	client = OpenAI(api_key=env.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

	xs = TRANSLATION_PROMPT
	xs += '\n\n'
	xs += sxml
	response = client.chat.completions.create(
	    model="deepseek-chat",
	    messages=[
	        {"role": "system", "content": "You are a helpful assistant"},
	        {"role": "user", "content": xs},
	    ],
		temperature=1.0,
		max_tokens=8192,
	    stream=False
	)
	print(response.usage)
	return response.choices[0].message.content


def get_token_count(x: str) -> int:
    import tiktoken
    encoding = tiktoken.encoding_for_model('gpt-4o')
    return len(encoding.encode(x))