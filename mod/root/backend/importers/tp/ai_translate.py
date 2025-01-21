import json
import subprocess
import requests
import httpx

from mod.lib.text import to_json, from_json

TEMPERATURE = 0.5
TOP_P = 0.8
TRANSLATION_PROMPT = """
Translate the entire XML document (except the element-tags) into SANSKRIT ONLY using the devanagari script (not Marathi/Hindi or other languages written using the same script).
This can be a partial, ill-formed document. So, do not add any additional text or explanations or missing nodes/tags.
Do not mess with the apostrophes, left-right quotation marks and other punctuation. 
""".strip()
def __translate(model: str, api_key: str, url: str, xml: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=url, timeout=httpx.Timeout(None))

    xs = TRANSLATION_PROMPT
    xs += '\n\n'
    xs += xml

    messages = [
        {"role": "system", "content": "You are a helpful assistant that translates entire XML documents from English into Classical Sanskrit while maintaining the structure of the document."},
        {"role": "user", "content": xs},
    ]

    q_content = ''

    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                top_p=TOP_P,
                temperature=TEMPERATURE,
                max_tokens=8192,
                stream=False
            )
            break
        except json.decoder.JSONDecodeError as e:
            print("ERROR. RETRYING")
    choice = response.choices[0]
    content = choice.message.content
    q_content += content
    print(f'PT: {response.usage.prompt_tokens}') #  [*{response.usage.prompt_cache_hit_tokens}/{response.usage.prompt_cache_miss_tokens}]
    print(f'CT: {response.usage.completion_tokens}')
    print(f'TT: {response.usage.total_tokens}')
    if choice.finish_reason == "length":
        print('-------------------------------------------------------')
        print(content)
        print('----------')
        q_content += '\n<DS-BREAK/>\n'
    return q_content

def __translate_curl(url: str, xml: str) -> str:
    prompt = ""
    prompt += "You are a helpful assistant that translates entire XML documents from English into Classical Sanskrit while maintaining the structure of the document."
    prompt += "\n\n"
    prompt += TRANSLATION_PROMPT
    prompt += '\n\n'
    prompt += xml

    params = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "stopSequences": [
                "Title"
            ],
            "temperature": TEMPERATURE,
            "maxOutputTokens": 8192,
            "topP": TOP_P
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=params)
    status_code = response.status_code
    text = from_json(response.text)
    print(status_code)
    print(text)



    # cmd = f"""
    #     curl '{url}'
    #   -H 'Content-Type: application/json'
    #   -X POST
    #   -d '{to_json(params)}'
    # """.replace("\n", " ").replace("  ", " ").strip()
    # status_code, text = subprocess.getstatusoutput(cmd)
    if status_code == 200:
        return text['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(status_code)

def gemini(xml: str):
    from mod.config import env
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={env.GOOGLE_AI_API_KEY}"
    return __translate_curl(url, xml)

def deepseek(xml: str):
    from mod.config import env
    return __translate('deepseek-chat', env.DEEPSEEK_API_KEY, 'https://api.deepseek.com', xml)

def hyperbolic_ds(xml: str):
    from mod.config import env
    return __translate('deepseek-ai/DeepSeek-V3', env.HYPERBOLIC_API_KEY, 'https://api.hyperbolic.xyz/v1', xml)

def get_token_count(x: str) -> int:
    import tiktoken
    encoding = tiktoken.encoding_for_model('gpt-4o')
    return len(encoding.encode(x))