import requests
from typing import Optional

# 读取 deno manual 文本 👇
Path = str
def get_text(path: Path) -> str:
    f = open(path, 'r')
    text = f.read()
    f.close()
    return text

def extract(line: str = None, file: Optional[Path] = None, category = None):
    if line:
        lines = [line]
    # ? processing...
    if file:
        text = get_text(file)
        lines = text.split("\n")              
    #
    response = requests.post(f"http://127.0.0.1:8000/extract/{category}", json={"lines": lines})
    object = response.json()
    #
    for (text, freq) in object["body"]:
        print(f'{text}\t{freq}')

