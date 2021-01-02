import spacy
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from spacy.matcher import Matcher
# 注意：rich 暂时不支持 markdown 内的 table 语法。
nlp = spacy.load("en_core_web_sm")
doc = nlp("He could defer his job to no one.")

header = "| " + " | ".join(['token', 'lemma', 'pos', 'pos?', 'tag', 'tag?', 'dep', 'dep?']) + " |" + "\n" 
sep = "------".join([" | " for i in range(9)]).strip() + "\n"
data = ""
for token in doc:
    text = token.text
    lemma = token.lemma_
    pos = token.pos_
    pos_meaning = spacy.explain(token.pos_)
    tag = token.tag_
    tag_meaning = spacy.explain(token.tag_)
    dep = token.dep_
    dep_meaning = str(spacy.explain(token.dep_))
    data += "| " + " | ".join([text, lemma, pos, pos_meaning, tag, tag_meaning, dep, dep_meaning]) + " |" + "\n"
result = header + sep + data

markdown = Markdown(result)
console = Console()
console.print(markdown)

# pattern = [{"POS": "NOUN"}, {"TAG": {"IN": ["WDT", "WP", "WP$"]}}]
def findClause(doc):
    matcher = Matcher(nlp.vocab)

    #pattern_1 = [{"DEP": "mark"}]
    #pattern_2 = [{"DEP": "cc"}]
    #matcher.add("mark", None, pattern_1)
    #matcher.add("cc", None, pattern_2)
    pattern = [{"DEP": "auxpass"}]
    matcher.add("passive", None, pattern)
    string = ""
    section_num = 0
    num = 0
    sents = [*doc.sents]
    print(len(sents))
    for sent in sents:
        matches = matcher(nlp(sent.text))
        '''matches_strings = [nlp.vocab.strings[match[0]] for match in matches]
        if len(matches) >= 3 and matches_strings.count("mark") >= 1 and matches_strings.count("cc") >= 2:'''
        if matches:
            section_num = section_num + 1
            string = string + f'#### {section_num}.\n'
            for match_id, start, end in matches:
                # Get string srepresentation
                span = sent[start:end]  # The matched span
                # print('relative clause modifier:', f'*{span.text}*', sep='\t')
                string = string + f'{nlp.vocab.strings[match_id]}:\t' + \
                    f'*{span.text}*\n'
                a = sent[:start].text + f' **{span.text}** ' + sent[end:].text
                num = num+1
                # print(str(num)+'.', a)
                string = string + str(num) + '. ' + a + '\n\n'
            # print('------------------------------------\n')
            string = string + '------------------------------------\n'
    return string
