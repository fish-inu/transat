import spacy
import pandas
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
doc = nlp("He could defer his job to no one.")

df = pandas.DataFrame([[token.text, token.lemma_, token.pos_, spacy.explain(token.pos_), token.tag_, spacy.explain(token.tag_), token.dep_, spacy.explain(
    token.dep_), token.shape_, token.is_alpha, token.is_stop] for token in doc], columns=['token', 'lemma', 'pos', 'pos?', 'tag', 'tag?', 'dep', 'dep?', 'shape', 'isAlpha', 'isStop'])

f = open('test.md', 'w')
df.to_markdown(f)
f.close()
#
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


def write2md(string):
    f = open('test.md', 'w')
    f.write(string)
    f.close()
