import numpy as np
import pandas as pd


def load_topic_data(topic_path, par_path):
    # 12 topics, top 15 words representing it
    topics = np.genfromtxt(topic_path, dtype=str, delimiter=",")[1:, 1:].T
    # load chapter text and lowercase it
    par_to_topics = pd.read_csv("data/gibbon_paragraphs_with_topics.csv")
    par_texts = np.char.lower(np.array(par_to_topics["StringText"], dtype=str))
    # make mapping 0-indexed
    par_to_topic = np.array(par_to_topics["LDA Topic"], dtype=int) - 1
    return topics, par_to_topic, par_texts
