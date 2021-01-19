import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Tuple
from collections.abc import Iterator
from src.load_model import init

nlp = init()
app = FastAPI()


class Text(BaseModel):
    content: str


@app.post("/parse/")
async def visualize(text: Text):
    from src.parse_line import parse_line
    body = parse_line(text.content, nlp)
    return {"body": body}


class Lines(BaseModel):
    lines: List[str]

@app.post("/extract/{category}")
async def nouns(category: str, lines: Lines):
    from src.extract_keywords import extract
    body: Iterator[Tuple[str, int]] = extract(lines.lines, nlp, category=category)
    return {
        "body": body
    }

if __name__ == "__main__":
    uvicorn.run(app)
