import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

def get_links(doc_links):
    links = []
    for i in doc_links:
        link_list = i.split('[')[1].split(']')[0].split(',')
        min_len = len(link_list[0])
        min_lnk = link_list[0]
        for link in link_list:
            if len(link) < min_len:
                min_len = len(link)
                min_lnk = link
        links.append(min_lnk.strip().split("'")[1])
    return links

def process_to_vectorize_documents(all_docs, nlp):
    all_tokens = []
    for i in range(len(all_docs)):
        all_tokens.append(nlp(all_docs[i]))
    all_tkn_stp_wrds = []
    for doc in all_tokens:
        tokens = ''
        for token in doc:
            if token.text not in nlp.Defaults.stop_words:
                tokens += ' ' + token.lemma_.lower()
        all_tkn_stp_wrds.append(tokens.strip())
    return all_tkn_stp_wrds


def vectorize_all_docs(all_tkn_stp_wrds, vectorizer):
    vectorizer.fit(all_tkn_stp_wrds)
    vectors = vectorizer.transform(all_tkn_stp_wrds)
    return vectors

def process_query(query, nlp):
    processed_query = ''
    for word in nlp(query):
        if word.text not in nlp.Defaults.stop_words:
            processed_query += ' ' + word.lemma_.lower()
    processed_query = processed_query.strip()
    return processed_query

def get_cosine_similarities(vectors, query_vector):
    cosine = cosine_similarity(vectors, query_vector)
    return cosine

def n_largest(cosines, n, thres):
    n_largest_indexes = np.argpartition(cosines.flatten(), -n)[-n:]
    largest_index_magnitude_dict = {}
    
    for i in n_largest_indexes:
        if cosines.flatten()[i] not in largest_index_magnitude_dict.keys():
            largest_index_magnitude_dict[cosines.flatten()[i]] = [i]
        else:
            largest_index_magnitude_dict[cosines.flatten()[i]].append(i)
    
    sorted_magnitudes = sorted(largest_index_magnitude_dict.keys(), reverse=True)
    
    indexes = []
    for i in sorted_magnitudes:
        if i > thres:
            indexes += largest_index_magnitude_dict[i]
    return indexes

def get_n_largest_indexes(cosine, n, thres):
    if cosine.max() > 0:
        indxs = n_largest(cosine, n, thres)
        if len(indxs) > 0:
            return indxs
        return -1
    else:
        return -1

def query_from(all_links, n, usr='student'):
    resultant_results = []
    count = 0
    for i in all_links:
        if usr.lower() == 'faculty' and 'student' not in i and 'employer' not in i:
            resultant_results.append(i)
            count += 1
        elif usr.lower() == 'employer' and 'student' not in i and 'faculty' not in i:
            resultant_results.append(i)
            count += 1
        elif usr.lower() == 'student' and 'faculty' not in i and 'employer' not in i:
            resultant_results.append(i)
            count += 1
        if count == n:
            break
    if len(resultant_results) > 0:
        return resultant_results
    else:
        return -1

def get_relevant_links(nlp, query, vectorizer, vectors, links, n=5, thres=0.1, usr="student"):
    flag = ("Resume".lower() in query) or ("Cover letter".lower() in query) or ("Networking".lower() in query) 
    flag = flag or ("Interview".lower() in query) or ("LinkedIn".lower() in query)

    query = query.replace('linkedin', 'LinkedIn')
    lower_than_upper_split = re.sub(r"([a-z\.!?])([A-Z])", r"\1 \2", query)
    upper_than_lower_split = re.sub(r"([A-Z\.!?]{2,})([A-Z]{1}[a-z]{2,})", r"\1 \2", lower_than_upper_split)
    bracket_before = re.sub(r"([)])([A-Z])", r"\1 \2", upper_than_lower_split)
    bracket_after = re.sub(r"([a-z])([(])", r"\1 \2", bracket_before)
    rmv_smbl = re.sub(r'[^A-Za-z\n@]', ' ', bracket_after)
    rmv_spcs = re.sub(r'\s{2,}', ' ', rmv_smbl)
    processed_query = process_query(rmv_spcs, nlp)
    query_vector = vectorizer.transform([processed_query])
    cosines = get_cosine_similarities(vectors, query_vector)
    index = get_n_largest_indexes(cosines, 40, thres)
    result_links = -1
    if index != -1:
        result_links = query_from(np.array(links)[index], n, usr)
    if result_links == -1:
        return (index, ['https://careers.humber.ca'])
    if flag and 'https://careers.humber.ca/resources-career.php' in result_links:
        result_links.remove('https://careers.humber.ca/resources-career.php')
        result_links = ['https://careers.humber.ca/resources-career.php'] + result_links
    elif flag:
        result_links = ['https://careers.humber.ca/resources-career.php'] + result_links      
    return (index, list(np.array(result_links)))