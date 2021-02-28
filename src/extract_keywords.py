# # # # # # # #
# ?  👇
# # # # # # # #

# 提取关键词
from collections import Counter
import re
from typing import Callable, Iterator, List, Tuple, Union
from spacy.tokens import Doc

###
# ? 提取名词
###

def extract_noun_by_line(line: Doc) -> Iterator[str]:
    for token in line:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
            yield token.lemma_

###
# ? 提取动词
###

def extract_verb_by_line(line: Doc) -> Iterator[str]:
    for token in line:
        if token.pos_ in ["VERB"] and not token.is_stop:
            yield token.lemma_

# # # # # # # #
# ? 提取介词短语 👇
# # # # # # # #


def extract_pp_by_line(line: Doc) -> Iterator[str]:
    for sent in line.sents:
        for token in sent.as_doc():
            if token.dep_ == "pobj":
                pobj = token
                prep = token.head
                pobj_index = pobj.i
                prep_index = prep.i
                phrase = f'{prep.text} {pobj.text}'
                if pobj_index > prep_index:
                    entire_phrase = " ".join(
                        [token.text for token in line[prep_index:pobj_index+1]])
                    yield entire_phrase
                else:
                    entire_phrase = " ".join(
                        [token.text for token in line[pobj_index:prep_index+1]])
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
        for token in sent.as_doc():
            if token.dep_ == "dobj":
                pobj = token
                prep = token.head
                pobj_index = pobj.i
                prep_index = prep.i
                phrase = f'{prep.text} {pobj.text}'
                if pobj_index > prep_index:
                    entire_phrase = " ".join(
                        [token.text for token in line[prep_index:pobj_index+1]])
                    yield entire_phrase
                else:
                    entire_phrase = " ".join(
                        [token.text for token in line[pobj_index:prep_index+1]])
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
# ? 提取缩略词 👇


def extract_abbr_by_line(line: Doc) -> Iterator[str]:
    for abbr in line._.abbreviations:
        yield f'{abbr}\t{abbr._.long_form}'
###

###
# ? 提取倒装句
###
def extract_inversion_by_line(line: Doc):
    for sent in line.sents:
        is_iver = False
        for token in sent.as_doc():
            if token.dep_ == "aux" or token.pos_ == "AUX":
                aux_index = token.i
                head = token.head
                neighbors = head.children
                for neighbor in neighbors:
                    if neighbor.dep_ == "nsubj" and 0 < neighbor.i - aux_index < 3:
                        is_iver = True
        if is_iver:
            yield (sent.text, 1)

###
# ? 提取 imperative 
###
def extract_imperative_by_line(line: Doc):
    for sent in line.sents:
        is_imperative = False
        for token in sent:
            dep = token.dep_
            tag = token.tag_
            if dep == "ROOT" and tag == "VB" and "nsubj" not in [child.dep_ for child in token.head.children]:
                is_imperative = True
                break
        if is_imperative:
            yield(sent.text, 1)
###
# ? 提取被动句                
###
def extract_passive_by_line(line: Doc):
    for sent in line.sents:
        is_passive = False
        for token in sent:
            dep = token.dep_
            if dep == "auxpass":
                is_passive = True
                break
        if is_passive:
            yield (sent.text, 1)

###
# ? 提取条件句 
###
class isCondition(Exception): pass
def extract_condition_by_line(line: Doc):
    for sent in line.sents:
        try:
            for token in sent.as_doc():
                if token.dep_ == "advcl":
                    if token.lower_ in ["provided", "providing", "suppose", "supposing"]:
                        raise isCondition
                    children = token.children
                    for child in children:
                        if child.lower_ in ["if", "unless", "when", "whenever", "anytime"]:
                            raise isCondition
                        elif child.lower_ == "as":
                            idx_before_as = child.i-1
                            if idx_before_as:
                                if sent[idx_before_as].lower_ == "long":
                                    raise isCondition
                            else:
                                continue
        except isCondition:      
            yield (sent.text, 1)

###
# ? 提取不定式 
###
def extract_infinitive_by_line(line: Doc):
    for sent in line.sents:
        is_infinitive = False
        for token in sent:
            if token.tag_ == "TO":
                is_infinitive = True
                break
        if is_infinitive:
            yield (sent.text, 1)

###
# ? 提取复合长句
###
def bold(token, string):
    if token.whitespace_ == " ":
        string += f"**{token.text}** "
    else:
        string += f"**{token.text_with_ws}**"

indicators = ["cc", "mark", "csubj", "csubjpass", "relcl", "advcl"]
def extract_cc_by_line(line: Doc) -> Iterator[Tuple[str, int]]:
    for sent in line.sents:
        cc_count = 0
        mark_count = 0
        relative_clauses = 0
        adverbial_clauses = 0
        non_finite_clauses= 0
        to_infinitives = 0
        clauses_as_subject = 0
        clauses_as_object = 0
        for token in sent:
            if token.dep_ == "cc":
                cc_count += 1
            elif token.dep_ == "mark":
                mark_count += 1
            elif token.dep_ == "relcl":
                relative_clauses += 1
            elif token.dep_ == "advcl":
                adverbial_clauses += 1
            elif token.dep_ == "acl":
                non_finite_clauses += 1
            elif token.tag_ == "TO":
                to_infinitives += 1
            elif token.dep_ in ["csubj", "csubjpass"]:
                clauses_as_subject += 1
            elif token.dep_ == "ccomp":
                clauses_as_object += 1
            else:
                continue
        count = cc_count + relative_clauses + adverbial_clauses +  non_finite_clauses + to_infinitives + clauses_as_object + clauses_as_subject                
        if count > 1:
            yield (sent.text, count)      

def extract_sentences_by_lines(lines: List[str], nlp, extract_by_line: Callable):
    for line in nlp.pipe(lines, batch_size=50):
        entries: Iterator[Tuple[str, int]] = extract_by_line(line)
        for sent, clauses_count in entries:
            yield (sent, clauses_count)

###
# ? resuable functions 👇
###

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


def extract_by_lines(lines: List[str], nlp, extract_by_line: Callable) -> Iterator[str]:
    for line in nlp.pipe(lines, batch_size=50):
        phrases = extract_by_line(line)
        for phrase in phrases:
            yield phrase

# ?主函数 👇
###


def extract(lines: List[str], nlp, use_dict=False, category=None):
    # extracting... 👇
    try:
        if category == "noun":
            terms: Iterator[str] = extract_by_lines(
                lines, nlp, extract_noun_by_line)
            result = count_terms(terms, use_dict)
            yield from result
        if category == "verb":
            terms: Iterator[str] = extract_by_lines(
                lines, nlp, extract_verb_by_line)
            result = count_terms(terms, use_dict)
            yield from result
        elif category == "np":
            terms: Iterator[str] = extract_by_lines(
                lines, nlp, extract_np_by_line)
            result = count_terms(terms, use_dict)
            yield from result
        elif category == "vp":
            terms: Iterator[str] = extract_by_lines(
                lines, nlp, extract_vb_by_line)
            result = count_terms(terms, use_dict)
            yield from result
        elif category == "pp":
            terms: Iterator[str] = extract_by_lines(
                lines, nlp, extract_pp_by_line)
            result = count_terms(terms, use_dict)
            yield from result
        elif category == "abbr":
            if nlp.pipe_names[-1] == "AbbreviationDetector":
                pass
            else:
                from .vendor.abbr import AbbreviationDetector
                abbreviation_pipe = AbbreviationDetector(nlp)
                nlp.add_pipe(abbreviation_pipe)
            terms: Iterator[str] = extract_by_lines(
                lines, nlp, extract_abbr_by_line)
            return count_terms(terms, use_dict)
        elif category == "compound-complex":
            result = extract_sentences_by_lines(lines, nlp, extract_cc_by_line)
            yield from sorted(result, key=lambda entry: entry[1], reverse=True)
        elif category == "inversion":
            result = extract_sentences_by_lines(lines, nlp, extract_inversion_by_line)
            yield from result 
        elif category == "imperative":
            result = extract_sentences_by_lines(lines, nlp, extract_imperative_by_line)
            yield from result 
        elif category == "passive":
            result = extract_sentences_by_lines(lines, nlp, extract_passive_by_line)
            yield from result 
        elif category == "condition":
            result = extract_sentences_by_lines(lines, nlp, extract_condition_by_line)
            yield from result 
        elif category == "infinitive":
            result = extract_sentences_by_lines(lines, nlp, extract_infinitive_by_line)
            yield from result 
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
