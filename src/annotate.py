from . import nlp

# TODO: 查看nlp.defaults 是否有 token_match
# 注意：rich 暂时不支持 markdown 内的 table 语法。

# 总结 askubuntu-posts 用时
# 11:23
def parse_file(file_path):
    with open(file_path) as infile: 
        for line in infile:
            if line.strip():
                doc = nlp(line.strip())
                for sent in doc.sents:
                    new_text = ""
                    for token in sent:
                        new_text += f"{token.text}_{token.dep_} "
                    print(new_text.strip())
parse_file("/home/fish/fish-backup/home/fish/search/exchange/temp")


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
