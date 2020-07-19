from modules.VisualFlickr import ImageAnalyzer
from modules.utils import serialize_results
from modules import graphical
import flickrapi
from modules.utils import download_file
import subprocess
import requests
from simple_term_menu import TerminalMenu
import os

TMP_USR_DIR_PIC = "./image_cache"
DEFAULT_USR_PIC = "./settings/buddyicon06_r.png"

HINT_USER_NAME = "visual.mvso"
HINT_USER_ID = "185900232@N03"

VALID_TERMINAL = "TERM" in os.environ


def yn_input_manual(req_msg, error_msg="Accepted answers: 'Y, N, y, n.'"):
    accepted_chars = ["Y", "y", "N", "n"]
    response = input(req_msg)
    while response not in accepted_chars:
        response = input(" ".join((error_msg, req_msg)))
    return response in accepted_chars[:2]


def string_input(req_msg, error_msg="Invalid input!", input_set=None):
    response = input(req_msg)
    while not response or input_set is not None and response not in input_set:
        response = input(" ".join((error_msg, req_msg)))
    return response


def insert_number(msg, error_msg="Value Error", integer_value=False, lower_bound=None, upper_bound=None,
                  bound_err_msg=None, print_human=None):
    while True:
        if print_human is not None:
            print_human_commands(print_human[0], print_human[1])
        try:
            value = int(input(msg)) if integer_value else float(input(msg))
            if lower_bound is not None and value < lower_bound or upper_bound is not None and value > upper_bound:
                if bound_err_msg is None:
                    print(error_msg)
                else:
                    print(bound_err_msg)
            else:
                return value
        except ValueError:
            print(error_msg)
        print()


def print_human_commands(methods, cols=4):
    for i, m in zip(range(len(methods)), methods):
        print("{:<4} {:<25}".format("[{0}]".format(i), m[0]), end="\n" if (i + 1) % cols == 0 else "")
    print("")


def try_index(msg, limit):
    try:
        index = int(input(msg))
        if 0 <= index < limit:
            return index
        else:
            raise ValueError
    except ValueError:
        return None


#################################

def print_columns(strings, cols=2):
    for i, m in zip(range(len(strings)), strings):
        print("{:<20}".format(m), end="\n" if (i + 1) % cols == 0 else "")
    print("")


def terminal_menu(req_msg, operations, index_return=False):
    operations = list(operations)
    c = TerminalMenu(operations, title=req_msg).show()
    return c if index_return or c is None else operations[c]


def yn_input(init_msg):
    global VALID_TERMINAL
    return terminal_menu(init_msg, ["Yes", "No"]) == "Yes" if VALID_TERMINAL else yn_input_manual(init_msg)


def users_file_insert():
    source_msg = "Insert the file name with user names or IDs: "
    store_msg = "Insert the name of the file in which store the results: "
    return input(source_msg), input(store_msg)


def user_id_insert(hint):
    user_id = input("Insert the user ID (hint: {}): ".format(hint))
    if yn_input("Print results on file? [Y/N]: "):
        return user_id, input("Insert the name of the file in which store the results: ")
    return user_id, None


def user_name_insert(hint):
    user_id = input("Insert the user name (hint: {}): ".format(hint))
    if yn_input("Print results on file? [Y/N]: "):
        return user_id, input("Insert the name of the file in which store the results: ")
    return user_id, None


def tags_file_insert():
    return input("Insert the file name > ")


def tags_insert(availability_method, hint, onto_name):
    tags = list()
    while True:
        inserted_tag = availability_method(string_input('Insert tag (hint: "{}"): '.format(hint)))
        if inserted_tag is None:
            print("Tag not available in {}. Retry.".format(onto_name))
        else:
            tags.append(inserted_tag)
            if not yn_input("Insert another tag? [Y/N]: "):
                break
    return tags


def show_tag_graphical(generator):
    w, image, pie_1, pie_2, text_3, text_4, text_5, button_1, _ = graphical.init_full_window(title_1="ORIGINAL TAGS "
                                                                                                     "DESCRIPTIVENESS",
                                                                                             title_2="ORIGINAL TAGS",
                                                                                             title_3="VISUAL TAGS")
    graphical.update_full(w, image, pie_1, pie_2, button_1, text_3, text_4, text_5, update_command=generator)


class CLI:
    __slots__ = "analyzer", "commands", "menu_showing"

    def __init__(self, mvso_settings_test, classifier_settings_test, flickr_settings_test, lang_option=True):
        print()
        print("+-+-+-+-+-+-+-+ VISUALFLICKR USER INTERFACE +-+-+-+-+-+-+-+")
        if lang_option:
            lang_welcome_msg = "------------------- AVAILABLE LANGUAGES -------------------"
            init_msg = "SELECT A LANGUAGE > "
            print()
            print(lang_welcome_msg)
            try:
                _ = os.environ["TERM"]
                languages = ["ENGLISH", "ITALIAN", "SPANISH", "FRENCH", "GERMAN", "CHINESE"]
                lang = terminal_menu(init_msg, languages)
                if lang is None:
                    self.exit()
            except (KeyError, subprocess.CalledProcessError) as e:
                global VALID_TERMINAL
                VALID_TERMINAL = False
                languages = [("ENGLISH",), ("ITALIAN",), ("SPANISH",), ("FRENCH",), ("GERMAN",), ("CHINESE",)]
                err_msg = "INSERT INTEGER VALUE IN RANGE 0 - {}".format(len(languages) - 1)
                lang = languages[
                    insert_number(init_msg, integer_value=True, lower_bound=0, upper_bound=len(languages) - 1,
                                  print_human=(languages, 2), bound_err_msg=err_msg)][0]
            lang = lang.lower()
            print("Inserted language: ", lang)
            print("-----------------------------------------------------------")
            print()
        else:
            lang = "english"
        core_welcome_msg = "------------------- CORE INITIALIZATION -------------------"
        print(core_welcome_msg)
        print("Loading modules...")
        self.analyzer = ImageAnalyzer(mvso_settings_test, classifier_settings_test, flickr_settings_test, lang=lang)
        self.commands = [("INSERT FILE NAME CONTAINING USER NAMES AND/OR USER IDS", "file_users"),
                         ("INSERT USER ID", "user_id"),
                         ("INSERT USER NAME", "user_name"),
                         ("INSERT FILE NAME CONTAINING LIST OF TAGS", "tags_file"),
                         ("INSERT TAGS", "manual_tags"),
                         ("EXIT", "exit")
                         ]
        print("Analyzer initialized with the language: ", self.analyzer.get_init_lang())
        print("All modules loaded.")
        print("Starting command interface...")
        print("-----------------------------------------------------------")
        print()

    def menu(self):
        global VALID_TERMINAL
        init_msg = "SELECT AN OPERATION > "
        err_msg = "INSERT INTEGER VALUE IN RANGE 0 - {}".format(len(self.commands) - 1)
        while True:
            print("------------------- AVAILABLE COMMANDS --------------------")
            try:
                if VALID_TERMINAL:
                    try:
                        _ = os.environ["TERM"]
                        x = terminal_menu(init_msg, [x[0] for x in self.commands], index_return=True)
                        if x is None:
                            self.exit()
                        else:
                            while True:
                                try:
                                    eval("self.{}".format(self.commands[x][1]))()
                                    break
                                except requests.exceptions.ConnectionError:
                                    print()
                                    if not yn_input("CONNECTION ERROR. RETRY? [Y/N]: "):
                                        raise
                    except (KeyError, subprocess.CalledProcessError):
                        VALID_TERMINAL = False
                else:
                    x = insert_number(init_msg, integer_value=True, lower_bound=0, upper_bound=len(self.commands) - 1,
                                      print_human=(self.commands, 1),
                                      bound_err_msg=err_msg)
                    while True:
                        try:
                            eval("self.{}".format(self.commands[x][1]))()
                            break
                        except requests.exceptions.ConnectionError:
                            print()
                            if not yn_input("CONNECTION ERROR. RETRY? [Y/N]: "):
                                raise
            except requests.exceptions.ConnectionError:
                self.exit()
            print("-----------------------------------------------------------")
            print()

    def file_users(self):
        source_file, store_file = users_file_insert()
        try:
            results = self.analyzer.analyze_users(source_file)
        except FileNotFoundError:
            print("File not found!")
            return
        serialize_results(results, store_file)

    def user_id(self):
        user_identifier, store_file = user_id_insert(HINT_USER_ID)
        try:
            results = self.analyzer.analyze_user_id(user_identifier)
            averages = self.analyzer.user_info_averages(results)
            if store_file is not None:
                serialize_results(results, store_file)
            usr_pic = self.user_pic_download(user_id=user_identifier)
            graphical.single_instance_window(title="USER ANALYSIS",
                                             image_emo=averages["image_emotion"],
                                             image_sent=averages["image_sentiment"],
                                             tags_emo=averages["tags_emotion"],
                                             tags_sent=averages["tags_sentiment"],
                                             tags_rel=averages["tags_reliability"],
                                             usr_img_path=(usr_pic, DEFAULT_USR_PIC),
                                             usr_id=user_identifier,
                                             usr_name=averages["user_name"])
            if usr_pic != DEFAULT_USR_PIC:
                try:
                    os.remove(usr_pic)
                except OSError:
                    pass
        except flickrapi.exceptions.FlickrError:
            print("User not found. Retry!")

    def user_name(self):
        name, store_file = user_name_insert(HINT_USER_NAME)
        try:
            user_id, results = self.analyzer.analyze_user_name(name)
            averages = self.analyzer.user_info_averages(results, user_id=user_id, user_name=name)
            if store_file is not None:
                serialize_results(results, store_file)
            usr_pic = self.user_pic_download(user_id=averages["user_id"])
            graphical.single_instance_window(title="USER ANALYSIS",
                                             image_emo=averages["image_emotion"],
                                             image_sent=averages["image_sentiment"],
                                             tags_emo=averages["tags_emotion"],
                                             tags_sent=averages["tags_sentiment"],
                                             tags_rel=averages["tags_reliability"],
                                             usr_img_path=(usr_pic, DEFAULT_USR_PIC),
                                             usr_id=averages["user_id"],
                                             usr_name=averages["user_name"])
            if usr_pic != DEFAULT_USR_PIC:
                try:
                    os.remove(usr_pic)
                except OSError:
                    pass
        except flickrapi.exceptions.FlickrError:
            print("User not found. Retry!")

    def user_pic_download(self, user_id):
        link = self.analyzer.get_user_pic(user_id)
        try:
            return download_file(link, TMP_USR_DIR_PIC, overwrite=False)
        except (RuntimeError, requests.exceptions.ConnectionError):
            return DEFAULT_USR_PIC

    def tags_file(self):
        file_name = tags_file_insert()
        try:
            tags = self.analyzer.analyze_tags_from_file(file_name, return_object="lines")
        except FileNotFoundError:
            print("File not found!")
            return
        tags = [x for x in tags if self.analyzer.check_availability(x) is not None]
        print("These are the inserted tags that are supported by {}:".format(self.analyzer.get_ontology_name()))
        print_columns(tags, 4)
        print()
        if yn_input("Continue with the showed tags? [Y/N]: "):
            generator = self.analyzer.analyze_tags(tags)
            show_tag_graphical(generator)

    def manual_tags(self):
        availability_method = self.analyzer.check_availability
        tags = tags_insert(availability_method, self.analyzer.get_label_hint(), self.analyzer.get_ontology_name())
        print("Inserted tags: {}".format(", ".join(tags)))
        generator = self.analyzer.analyze_tags(tags)
        show_tag_graphical(generator)

    def exit(self):
        print("Exiting from VisualFlickr...")
        if yn_input("Clear cache? [Y/N]: "):
            self.analyzer.clear_cache()
            print("Cache cleared.")
        print("-----------------------------------------------------------")
        exit()


def start_interface():
    mvso_settings_test = "./settings/MVSO_settings.json"
    classifier_settings_test = "./settings/classifier_settings.json"
    flickr_settings_test = "./settings/flickr_settings.json"
    cli = CLI(mvso_settings_test, classifier_settings_test, flickr_settings_test)
    cli.menu()


if __name__ == "__main__":
    averages_t = {'user_id': '7488735@N03', 'user_name': 'raoul.bizzotto',
                  'image_sentiment': {'sentiment': 0.045999999999999999},
                  'image_emotion': {'ecstasy': 0.017999999999999999, 'joy': 0.091999999999999998,
                                    'serenity': 0.050999999999999997, 'admiration': 0.017999999999999999,
                                    'trust': 0.040000000000000001, 'acceptance': 0.017999999999999999,
                                    'terror': 0.029000000000000001, 'fear': 0.040000000000000001,
                                    'apprehension': 0.014999999999999999, 'amazement': 0.16,
                                    'surprise': 0.041000000000000002, 'distraction': 0.019,
                                    'grief': 0.025000000000000001,
                                    'sadness': 0.088999999999999996, 'pensiveness': 0.025999999999999999,
                                    'loathing': 0.016, 'disgust': 0.025000000000000001, 'boredom': 0.042999999999999997,
                                    'rage': 0.023, 'anger': 0.055, 'annoyance': 0.027,
                                    'vigilance': 0.014999999999999999,
                                    'anticipation': 0.025000000000000001, 'interest': 0.089999999999999997},
                  'tags_reliability': 1.429, 'tags_sentiment': {}, 'tags_emotion': {}}
    graphical.single_instance_window(title="USER ANALYSIS", image_emo=averages_t["image_emotion"],
                                     image_sent=averages_t["image_sentiment"], tags_emo=averages_t["tags_emotion"],
                                     tags_sent=averages_t["tags_sentiment"],
                                     tags_rel=averages_t["tags_reliability"],
                                     usr_img_path="../image_test/birds.jpg", usr_id=averages_t["user_id"],
                                     usr_name=averages_t["user_name"])
