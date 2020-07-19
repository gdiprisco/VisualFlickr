import csv
import json
from numpy import around as rd
from collections import defaultdict


class FieldNamesException(Exception):
    def __init__(self):
        super().__init__("Not valid fieldnames")


class LangException(Exception):
    def __init__(self):
        super().__init__("Ontology not available with the inserted language.")


class Ontology:
    __slots__ = "type", "sentiment", "emotion", "language"

    def __init__(self, onto_type="MVSO", language="english"):
        self.type = onto_type
        self.sentiment = dict()
        self.emotion = dict()
        self.language = language

    @classmethod
    def parse_settings(cls, settings_path, lang="english"):
        with open(settings_path, 'r') as settings_file:
            try:
                settings = json.load(settings_file)[lang]
            except KeyError:
                raise LangException
            sentiment_csv_file = settings["sentiment_csv"]
            emotion_csv_file = settings["emotion_csv"]
            onto = Ontology(language=lang)
            onto.add_sentiment(sentiment_csv_file)
            onto.add_emotion(emotion_csv_file)
        return onto

    def search_similar(self, adj=None, noun=None):
        pass

    def add_sentiment(self, csv_sentiment):
        fieldnames = ("ANP", "sentiment")
        self.sentiment = Ontology.csv_to_dictionary(csv_sentiment, fieldnames=fieldnames)
        return self.sentiment

    def add_emotion(self, csv_emotion):
        self.emotion = Ontology.csv_to_dictionary(csv_emotion, first_line_header=True)
        return self.emotion

    def get_sentiment(self):
        return self.sentiment

    def get_emotion(self):
        return self.emotion

    def get_type(self):
        return self.type

    def get_lang(self):
        return self.language

    def get_labels(self):
        return set(self.sentiment.keys()) & set(self.get_emotion().keys())

    def get_sentiment_of_pairs(self, pairs):
        if len(pairs):
            if isinstance(pairs, list) or isinstance(pairs, set):
                tmp_sentiment = defaultdict(list)
                for pair in pairs:
                    for sentiment_key, score in self.sentiment[pair].items():
                        tmp_sentiment[sentiment_key].append(float(score))
                return {sent_key: rd(sum(s_list) / len(s_list), 3) for sent_key, s_list in tmp_sentiment.items()}
            return self.sentiment[pairs]
        return None

    def get_emotion_of_pairs(self, pairs):
        if len(pairs):
            if isinstance(pairs, list) or isinstance(pairs, set):
                tmp_emotion = defaultdict(list)
                for pair in pairs:
                    for emotion_key, score in self.emotion[pair].items():
                        tmp_emotion[emotion_key].append(float(score))
                return {emo_key: rd(sum(s_list) / len(s_list), 3) for emo_key, s_list in tmp_emotion.items()}
            else:
                return self.emotion[pairs]
        return None

    @classmethod
    def csv_to_dictionary(cls, csv_file, first_line_header=False, fieldnames=None):
        """
        fieldnames = ("ANP", "ecstasy", "joy", "serenity", "admiration", "trust", "acceptance", "terror", "fear",
                      "apprehension", "amazement", "surprise", "distraction", "grief", "sadness", "pensiveness",
                      "loathing", "disgust", "boredom", "rage", "anger", "annoyance", "vigilance", "anticipation",
                      "interest")
        :param csv_file: csv_file path
        :param first_line_header: if csv file contains header
        :param fieldnames: fieldnames necessary if csv doesn't contain header
        :return: dictionary
        {
            "header1":{
                "prop1" : val1,
                "prop2" : val2
                }
        }
        """
        scores = {}
        with open(csv_file, 'r') as csv_pointer:
            if first_line_header:
                csv_reader = csv.reader(csv_pointer)
                fieldnames = tuple(next(csv_reader))
            elif not isinstance(fieldnames, tuple):
                raise FieldNamesException
            header = fieldnames[0]
        with open(csv_file, 'r') as csv_pointer:
            for row in csv.DictReader(csv_pointer, fieldnames):
                if first_line_header is True:
                    first_line_header = False
                else:
                    key = row[header]
                    temp_values = {}
                    for k, v in list(row.items())[1:]:
                        temp_values[k] = v
                    scores[key] = temp_values
        return scores


if __name__ == "__main__":
    emotion_csv_file_t= '../mvso_scores/ANP_emotion_scores/ANP_emotion_mapping_english.csv'
    sentiment_csv_file_t = '../mvso_scores/mvso_sentiment/english.csv'
    emotion = Ontology.csv_to_dictionary(emotion_csv_file_t, first_line_header=True)
    sentiment = Ontology.csv_to_dictionary(sentiment_csv_file_t, fieldnames=("ANP", "sentiment"))
    for anp in emotion.keys():
        print(anp)
    input("INSERT ANY KEY TO CONTINUE...")
    for anp in sentiment.keys():
        print(anp)
    input("INSERT ANY KEY TO CONTINUE...")
    for anp, dict_emotion in emotion.items():
        print(anp, dict_emotion)
    input("INSERT ANY KEY TO CONTINUE...")
    for anp, dict_sentiment in sentiment.items():
        print(anp, dict_sentiment)
