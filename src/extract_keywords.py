# # # # # # # #
# ?  👇
# # # # # # # #

# 提取关键词
from collections import Counter
import re
from typing import Iterator, List, Tuple, Dict, Union
from spacy.tokens import Doc

# 读取英汉大辞典
def get_dict() -> Iterator[Tuple[str, str]]:
    f = open('test/英汉大词典.txt', 'r')
    lines = f.readlines()
    f.close()
    for entry in lines:
        parts = entry.strip().split("\t")
        yield (parts[0], parts[1])

def count_terms(terms: Iterator[str], use_dict) -> Union[Iterator[Tuple[str, int]], Iterator[Tuple[str, str, int]]]:
    counter = Counter(terms)
    line: Tuple[str, int]
    for line in counter.most_common():
        term = line[0]
        freq = line[1]
        if use_dict:
            definitions: List = [parts[1]
                                    for parts in get_dict() if term == parts[0]]
            if not definitions:
                yield (term, term, freq)
            else:
                yield (term, " --delimiter-- ".join(definitions), freq)
        else:
            yield (term, freq)

###
# ? 提取缩略词
###

###
# ? 提取名词
###
def extract_noun_by_lines(lines: List[str], nlp) -> Iterator[str]:
    line: Doc
    for line in nlp.pipe(lines, batch_size=50):
        nouns = extract_noun_by_line(line)
        for noun in nouns:
            yield noun

def extract_noun_by_line(line: Doc) -> Iterator[str]:
    for token in line:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and not token.is_punct and token.is_alpha:
            yield token.lemma_

# # # # # # # #
# ? 提取介词短语 👇
# # # # # # # #

def extract_pp_by_lines(lines: List[str], nlp) -> Iterator[str]:
    for line in nlp.pipe(lines, batch_size=50):
        line: Doc
        phrases = extract_pp_by_line(line)
        for phrase in phrases:
            yield phrase

def extract_pp_by_line(line: Doc) -> Iterator[str]:
    for sent in line.sents:
        for token in sent:
            if token.dep_ == "pobj":
                pobj = token
                prep = token.head
                pobj_index = pobj.i
                prep_index = prep.i
                phrase = f'{prep.text} {pobj.text}'
                if pobj_index > prep_index:
                    entire_phrase = " ".join([token.text for token in line[prep_index:pobj_index+1]])
                    yield entire_phrase
                else:
                    entire_phrase = " ".join([token.text for token in line[pobj_index:prep_index+1]])
                    yield entire_phrase

###
# ? 提取动词短语 👇
###
def extract_vb_by_lines(lines: List[str], nlp) -> Iterator[str]:
    for line in nlp.pipe(lines, batch_size=50):
        line: Doc
        phrases = extract_vb_by_line(line)
        for phrase in phrases:
            yield phrase

def extract_vb_by_line(line: Doc) -> Iterator[str]:
    for sent in line.sents:
        for token in sent:
            if token.dep_ == "dobj":
                pobj = token
                prep = token.head
                pobj_index = pobj.i
                prep_index = prep.i
                phrase = f'{prep.text} {pobj.text}'
                if pobj_index > prep_index:
                    entire_phrase = " ".join([token.text for token in line[prep_index:pobj_index+1]])
                    yield entire_phrase
                else:
                    entire_phrase = " ".join([token.text for token in line[pobj_index:prep_index+1]])
                    yield entire_phrase

###
# ?提取名词短语 👇
###

def extract_np_by_lines(lines: List[str], nlp) -> Iterator[str]:
    line: Doc
    for line in nlp.pipe(lines, batch_size=50):
        phrases = extract_np_by_line(line)
        for phrase in phrases:
            yield phrase

def extract_np_by_line(line: Doc) -> Iterator[str]:
    for sent in line.sents:
        for np in sent.noun_chunks:
            if len(np) > 1:
                yield np.text

###  
# ?主函数 👇
###
def extract(lines: List[str], nlp, use_dict=False, category=None):
    # extracting... 👇
    try:
        if category == "noun":
            nouns_ = extract_noun_by_lines(lines, nlp)
            return count_terms(nouns_, use_dict)
        if category == "pp":
            phrases = extract_pp_by_lines(lines, nlp)
            return count_terms(phrases, use_dict)
        if category == "vp":
            phrases = extract_vb_by_lines(lines, nlp)
            return count_terms(phrases, use_dict)
        if category == "np":
            phrases = extract_np_by_lines(lines, nlp)
            return count_terms(phrases, use_dict)
    except:
        from rich.console import Console
        console = Console()
        console.print_exception()


def temp():
    if not any([nouns, verbs, ners, noun_chunks]):
        return "都不生成，你玩个蛋"
    verbs = [token.lemma_ for token in doc if token.pos_ ==
             'VERB' and not token.is_stop and not token.is_punct and token.is_alpha]
    chunks = [chunk.text for chunk in doc.noun_chunks if chunk.__len__(
    ) > 1 and re.match(r'[a-zA-Z ]+', chunk.text)]
    named_entities = [ent.text for ent in doc.ents]
    # count them
    vs = Counter(verbs)
    chs = Counter(chunks)
    ner = Counter(named_entities)
    with open('./verbs.txt', 'w') as f:
        for w in vs.most_common():
            if w[1] > 1:
                defs = [entry[1] for entry in dicts if w[0] == entry[0]]
                if not defs:
                    defs = w[0]
                    f.write(f'{w[0]}\t{defs}\t{w[1]}\n')
                else:
                    f.write(
                        f'{w[0]}\t{" --delimiter-- ".join(defs)}\t{w[1]}\n')
    with open('./chunks.txt', 'w') as f:
        for w in chs.most_common():
            if w[1] > 1:
                defs = [entry[1] for entry in dicts if w[0] == entry[0]]
                if not defs:
                    defs = w[0]
                    f.write(f'{w[0]}\t{defs}\t{w[1]}\n')
                else:
                    f.write(
                        f'{w[0]}\t{" --delimiter-- ".join(defs)}\t{w[1]}\n')
    with open('./NER.txt', 'w') as f:
        for w in ner.most_common():
            if w[1] > 1:
                defs = [entry[1] for entry in dicts if w[0] == entry[0]]
                if not defs:
                    defs = w[0]
                    f.write(f'{w[0]}\t{defs}\t{w[1]}\n')
                else:
                    f.write(
                        f'{w[0]}\t{" --delimiter-- ".join(defs)}\t{w[1]}\n')


# 中文
""" def cn():
    import jieba.posseg as pseg
    words = pseg.cut(text)
    res = [w for w, p in words if p in ['v', 'ns', 'n']]
    c = Counter(res)
    # with open('/home/fish/中文术语.txt', 'a') as f:
    #    for w in c.most_common():
    #        f.write(f'{w[0]}\t{w[1]}\n')
    result = [item for item in c.most_common() if item[1] > 1]
    print(result) """
