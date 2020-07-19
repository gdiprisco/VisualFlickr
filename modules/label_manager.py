import numpy as np
import random


class LabelManager:

    def __init__(self, labels_file):
        self.entire_labels = set(np.loadtxt(labels_file, str, delimiter='\t'))
        self.adjectives, self.nouns = LabelManager.bipartite_labels(self.entire_labels)

    def get_entire_labels(self):
        return self.entire_labels

    def get_adjectives(self):
        return self.adjectives

    def get_nous(self):
        return self.nouns

    def get_all_labels(self):
        return self.entire_labels.union(self.adjectives, self.nouns)

    @classmethod
    def bipartite_labels(cls, labels, splitter="_"):
        former, latter = set(), set()
        for label in labels:
            former.add(label.split(splitter)[0])
            latter.add(label.split(splitter)[1])
        return former, latter


class UniqueLabelManager:
    __slots__ = "unique_labels"

    def __init__(self, alpha_labels, beta_labels):
        self.unique_labels = dict()
        self.unique_labels.update([(x.replace("_", ""), x) for x in set(alpha_labels).intersection(beta_labels)])

    def get_labels(self, flattened_too=False):
        labels = set(self.unique_labels.values())
        if flattened_too:
            return labels.union(set(self.unique_labels.keys()))
        return labels

    def __contains__(self, item):
        return True if self.intersection(item) else False

    def __str__(self):
        return str(self.unique_labels.values())

    def intersection(self, item):
        return set(self.unique_labels.values()).intersection(set(item))

    def intersection_and_difference(self, item):
        item_set = set(item)
        unique_labels = set(self.unique_labels.values())
        intersection = unique_labels & item_set
        difference = item_set - unique_labels
        return intersection, difference

    def disjoint(self, labels):
        if not isinstance(labels, list):
            labels = [labels]
        for index, flat in enumerate(labels):
            if flat in self.unique_labels:
                labels[index] = self.unique_labels[flat]

    def check_availability(self, label):
        if label in self.unique_labels.values():
            return label
        elif label in self.unique_labels:
            return self.unique_labels[label]
        else:
            return None

    def get_random_label(self):
        return random.choice(list(self.unique_labels.values()))


if __name__ == "__main__":
    paired_labels = ["eternal_city",
                     "old_buses",
                     "sacred_music",
                     "long_jetty",
                     "stone_statue",
                     "holy_ground",
                     "gothic_building",
                     "lost_souls",
                     "visual_emotion",
                     "good_eye",
                     "elite_woman",
                     "abandoned_industry",
                     "tiny_lights"]
    minimal_labels = ["lost_souls",
                      "visual_emotion",
                      "good_eye",
                      "old_buses",
                      "sacred_music",
                      "marry_christmas"]
    ulm = UniqueLabelManager(paired_labels, paired_labels)
    print(ulm)
    print(ulm.intersection_and_difference(minimal_labels))
    print("INTERSECTION: ", ulm.intersection(minimal_labels))
    print("CONTAIN: ", minimal_labels in ulm)
    joints = ["lostsouls", "goodeye"]
    ulm.disjoint(joints)
    print(joints)
    j_and_unj = ["lostsouls", "goodeye", "sacred_music", "america"]
    for i in j_and_unj:
        print(ulm.check_availability(i))
