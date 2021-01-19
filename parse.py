from rich.console import Console
from rich.table import Table
import requests

def parse(text):
    response = requests.post(f"http://127.0.0.1:8000/parse/", json={'content': text})
    sents = response.json()

    console = Console()
    for sent in sents['body']:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("token")
        table.add_column("lemma")
        table.add_column("pos")
        table.add_column("tag")
        table.add_column("dep")
        for token in sent:
            table.add_row(token['word'], token['lemma'], token['pos'], token['tag'], token['dep'])
        console.print(table)

