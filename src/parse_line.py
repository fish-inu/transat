from spacy import explain

def parse_line(text, nlp):
    doc = nlp(text)
    for sent in doc.sents:
        yield parse_sent(sent)


def parse_sent(sent):
    for token in sent:
        word = token.text
        lemma = token.lemma_
        pos = token.pos_
        pos_meaning = explain(token.pos_)
        tag = token.tag_
        tag_meaning = explain(token.tag_)
        dep = token.dep_
        dep_meaning = str(explain(token.dep_))
        head = token.head.text
        yield {
            'word': word,
            'lemma': lemma,
            'pos': f'{pos} -> {pos_meaning}',
            'tag': f'{tag} -> {tag_meaning}',
            'dep': f'{dep} -> {dep_meaning}',
            'head': head
        }