from modules.pacmanprogressbar import Pacman
import json
from collections import defaultdict
from numpy import around as rd
from modules import utils
from modules.classifier import Classifier
from modules.ontology_manager import Ontology
from modules.flickr_manager import FlickrSet
from modules.label_manager import UniqueLabelManager

IMAGE_TMP = "./image_cache"
EXTENSION = ".jpg"


class ImageAnalyzer(object):
    __slots__ = "onto", "classifier", "image_manager", "unique_labels", "image_cache_dir", "language", "progressbar"

    def __init__(self, mvso_settings, classifier_settings, flickr_settings, image_cache_dir=None, lang="english"):
        self.onto = Ontology.parse_settings(mvso_settings, lang=lang)
        self.classifier = Classifier.parse_settings(classifier_settings, lang=lang)
        self.image_manager = FlickrSet(flickr_settings, temp_directory="image_cache", image_size="default")
        self.unique_labels = UniqueLabelManager(self.classifier.get_labels(), self.onto.get_labels())
        self.image_cache_dir = IMAGE_TMP if image_cache_dir is None else image_cache_dir
        self.language = lang
        self.progressbar = True

    def get_ontology_name(self):
        return self.onto.get_type()

    def get_all_labels(self, flattened_too=False):
        return self.unique_labels.get_labels(flattened_too)

    def get_label_hint(self):
        return self.unique_labels.get_random_label()

    def get_init_lang(self):
        return self.language

    def check_availability(self, label):
        return self.unique_labels.check_availability(label)

    def analyze_user_id(self, user_id):
        user_data = self.image_manager.get_data_from_id(user_id)
        return self.analyze_dict_of_images(user_data)

    def analyze_user_name(self, user_name):
        user_id, user_data = self.image_manager.get_data_from_name(user_name)
        return user_id, self.analyze_dict_of_images(user_data)

    def analyze_users(self, users_source_file):
        analysis_results = dict()
        with open(users_source_file, 'r') as users_file:
            users = json.load(users_file)
            try:
                un_targets = users["users_name"]
            except KeyError:
                un_targets = []
            try:
                id_targets = users["users_id"]
            except KeyError:
                id_targets = []
        for user_name in un_targets:
            user_id, user_results = self.analyze_user_name(user_name)
            analysis_results[user_id] = user_results
        for user_id in id_targets:
            analysis_results[user_id] = self.analyze_user_id(user_id)
        return analysis_results

    def analyze_dict_of_images(self, data_dict, read_cache=True, store_cache_mode=True):
        # data_dict = {list(data_dict.keys())[0]: list(data_dict.values())[0]} # ONLY FOR TEST PURPOSE
        data_size = len(data_dict)
        if self.progressbar:
            progressbar = Pacman(end=100, text="Analysis", width=50)
            print()
            progressbar.update(0)
        for image_id, image_data in data_dict.items():
            tags_sentiment, tags_emotion, tags_reliability, image_sentiment, image_emotion = self.analyze(
                image_id, image_data, read_cache, store_cache_mode)
            data_dict[image_id]["VisualFlickr"] = dict()
            data_dict[image_id]["VisualFlickr"]["image_sentiment"] = image_sentiment
            data_dict[image_id]["VisualFlickr"]["image_emotion"] = image_emotion
            data_dict[image_id]["VisualFlickr"]["tags_reliability"] = tags_reliability
            data_dict[image_id]["VisualFlickr"]["tags_sentiment"] = tags_sentiment
            data_dict[image_id]["VisualFlickr"]["tags_emotion"] = tags_emotion
            if 'progressbar' in locals():
                progressbar.update(100 / data_size)
        return data_dict

    def user_info_averages(self, data_dict, user_id=None, user_name=None):
        data = dict()
        if user_id is not None or user_name is not None:
            data["user_id"] = self.image_manager.get_user_id(user_name) if user_id is None else user_id
            data["user_name"] = self.image_manager.get_user_name(user_id) if user_name is None else user_name
        data["image_sentiment"] = defaultdict(list)
        data["image_emotion"] = defaultdict(list)
        data["tags_reliability"] = list()
        data["tags_sentiment"] = defaultdict(list)
        data["tags_emotion"] = defaultdict(list)
        for _, nested in data_dict.items():
            if isinstance(nested["VisualFlickr"]["image_sentiment"], dict):
                for k, v in nested["VisualFlickr"]["image_sentiment"].items():
                    data["image_sentiment"][k].append(v)
            if isinstance(nested["VisualFlickr"]["image_emotion"], dict):
                for k, v in nested["VisualFlickr"]["image_emotion"].items():
                    data["image_emotion"][k].append(v)
            if nested["VisualFlickr"]["tags_reliability"] is not None:
                data["tags_reliability"].append(nested["VisualFlickr"]["tags_reliability"])
            if isinstance(nested["VisualFlickr"]["tags_sentiment"], dict):
                for k, v in nested["VisualFlickr"]["tags_sentiment"].items():
                    data["tags_sentiment"][k].append(v)
            if isinstance(nested["VisualFlickr"]["tags_emotion"], dict):
                for k, v in nested["VisualFlickr"]["tags_emotion"].items():
                    data["tags_emotion"][k].append(v)
        data["image_sentiment"] = {k: rd(sum(v) / len(v), 3) for k, v in data["image_sentiment"].items()}
        data["image_emotion"] = {k: rd(sum(v) / len(v), 3) for k, v in data["image_emotion"].items()}
        data["tags_reliability"] = rd(sum(data["tags_reliability"]) / len(data["tags_reliability"]), 3)
        data["tags_sentiment"] = {k: rd(sum(v) / len(v), 3) for k, v in data["tags_sentiment"].items()}
        data["tags_emotion"] = {k: rd(sum(v) / len(v), 3) for k, v in data["tags_emotion"].items()}
        return data

    def analyze(self, image_id, image_data, read_cache=True, store_cache_mode=True, all_info=False):
        image_name = image_id + EXTENSION
        image_file = utils.download_file(image_data['download_link'], IMAGE_TMP, image_name, overwrite=not read_cache)
        visual_tags = list(self.classifier.classify_image(image_file))
        if not store_cache_mode:
            utils.remove_file(image_file)
        image_sentiment = self.onto.get_sentiment_of_pairs(visual_tags)
        image_emotion = self.onto.get_emotion_of_pairs(visual_tags)
        original_tags = [element.replace(" ", "_").lower() for element in image_data['tags']]
        self.unique_labels.disjoint(original_tags)
        tags_in_onto, tags_out_onto = self.unique_labels.intersection_and_difference(original_tags)
        tags_sentiment = self.onto.get_sentiment_of_pairs(tags_in_onto)
        tags_emotion = self.onto.get_emotion_of_pairs(tags_in_onto)
        tags_reliability = utils.reliability_score(visual_tags, tags_in_onto, tags_out_onto)
        if all_info:
            return tags_sentiment, tags_emotion, tags_reliability, image_sentiment, image_emotion, image_data[
                "title"], image_file, original_tags, visual_tags
        return tags_sentiment, tags_emotion, tags_reliability, image_sentiment, image_emotion

    def analyze_tags_from_file(self, tags_file, return_object="operation"):
        with open(tags_file) as f:
            tags = f.read().splitlines()
        if return_object == "operation":
            return self.analyze_tags(tags)
        elif return_object == "lines":
            return tags
        else:
            return None

    def analyze_tags(self, tags):
        """
        Returns image_sentiment, image_emotion, tags_reliability, tags_sentiment, tags_emotion, title, path,
        original_tags, visual_tags
        :param tags: list of strings
        :return: tuple
        """
        tags = self.unique_labels.intersection(tags)
        for image_id, image_data in self.image_manager.get_image_from_tags(tags):
            data = self.analyze(image_id, image_data, read_cache=True, store_cache_mode=True, all_info=True)
            yield data

    def clear_cache(self):
        self.image_manager.remove_temp_images()

    def get_user_pic(self, user_id):
        return self.image_manager.get_user_pic_link(user_id)


if __name__ == "__main__":
    SEARCH_FOR = "tags"  # "users"
    mvso_settings_test = "settings/MVSO_settings.json"
    classifier_settings_test = "settings/classifier_settings.json"
    flickr_settings_test = "settings/flickr_settings.json"
    users_list_test = "settings/users.json"
    results_filename = 'results/results.json'
    tags_filename = "settings/tags.txt"

    analyzer = ImageAnalyzer(mvso_settings_test, classifier_settings_test, flickr_settings_test)

    if SEARCH_FOR == "tags":
        data_sem = ["image_sentiment", "image_emotion", "tags_reliability", "tags_sentiment", "tags_emotion", "title",
                    "original_tags", "visual_tags"]
        for x in analyzer.analyze_tags_from_file(tags_filename):
            for lab, k_l in zip(data_sem, x):
                print(lab, k_l)
            key = input("INSERT Q to QUIT. ANY STRING TO CONTINUE > ")
            if key == "Q" or key == "q":
                break
    elif SEARCH_FOR == "users":
        results = analyzer.analyze_users(users_list_test)
        utils.serialize_results(results, results_filename)
