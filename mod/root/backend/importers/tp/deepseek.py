# set up deep seek translation pipeline
from mod.config import env

TRANSLATION_PROMPT = """
Translate the entire XML document (except the element-tags) into SANSKRIT ONLY (not Marathi/Hindi or other languages written using the devanagari script).
This can be a partial, ill-formed document. So, do not add any additional text or explanations or missing nodes/tags.
Do not mess with the apostrophes, left-right quotation marks and other punctuation. 
""".strip()
def translate(sxml: str) -> str:
	from openai import OpenAI
	client = OpenAI(api_key=env.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

	xs = TRANSLATION_PROMPT
	xs += '\n\n'
	xs += sxml

	messages = [
		{"role": "system", "content": "You are a helpful assistant that translates entire XML documents from English into Classical Sanskrit while maintaining the structure of the document."},
		{"role": "user", "content": xs},
	]

	q_content = ''
	TEMPERATURE = 0.5
	TOP_P = 0.8
	while True:
		response = client.chat.completions.create(
			model="deepseek-chat",
			messages=messages,
			top_p=TOP_P,
			temperature=TEMPERATURE,
			max_tokens=8192,
			stream=False
		)
		choice = response.choices[0]
		content = choice.message.content
		q_content += content
		print(f'PT: {response.usage.prompt_tokens} [*{response.usage.prompt_cache_hit_tokens}/{response.usage.prompt_cache_miss_tokens}]')
		print(f'CT: {response.usage.completion_tokens}')
		print(f'TT: {response.usage.total_tokens}')
		if choice.finish_reason == "length":
			print('-------------------------------------------------------')
			print(content)
			print('----------')
			q_content += '<DS-BREAK/>'
			ui = input("More tokens to come. Continue? [*y/n]")
			if ui == "n":
				break
			messages.append({"role": "system", "content": content})
			messages.append({"role": "user", "content": "CONTINUE. Remember that you are translating an XML document. So be mindful of where you are in the hierarchy."})
		else:
			break
	return q_content


def get_token_count(x: str) -> int:
    import tiktoken
    encoding = tiktoken.encoding_for_model('gpt-4o')
    return len(encoding.encode(x))