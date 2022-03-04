import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# 12 topics, top 15 words representing it
nmf_topics = np.genfromtxt("data/gibbon_chapters_topics_nmf.csv", dtype=str,
                           delimiter=",")[1:, 1:].T
lda_topics = np.genfromtxt("data/gibbon_chapters_topics_lda.csv", dtype=str,
                           delimiter=",")[1:, 1:].T
# load chapter text and lowercase it
par_to_topics = pd.read_csv("data/gibbon_paragraphs_with_topics.csv")
par_texts = np.char.lower(np.array(par_to_topics["StringText"], dtype=str))
# make mapping 0-indexed
par_to_nmf = np.array(par_to_topics["NMF Topic"], dtype=int) - 1
par_to_lda = np.array(par_to_topics["LDA Topic"], dtype=int) - 1
# check how many paragraphs with have words associated with topic label in them
nmf_score = []
lda_score = []
for i, par_text in enumerate(par_texts):
    for topics, par_to_topic, score in [(nmf_topics, par_to_nmf, nmf_score),
                                        (lda_topics, par_to_lda, lda_score)]:
        topic = topics[par_to_topic[i]]
        if par_to_topic[i] == 0:
            count = 0
            for word in topic:
                count += par_text.count(word)
            score.append(count)
# plot score results
for score in [nmf_score, lda_score]:
    plt.hist(score, np.arange(0, max(score)))
    plt.yscale("log")
    plt.show()
