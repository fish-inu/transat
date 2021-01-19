import re
import spacy

def init():
    nlp = spacy.load("en_core_web_lg")
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer, before="parser")
    nlp.tokenizer.token_match = re.compile("/.*?(?=[/ \n])").match
    nlp.tokenizer.infix_finditer = spacy.util.compile_infix_regex(nlp.Defaults.infixes).finditer
    return nlp
