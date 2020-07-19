import os
import numpy as np
import json


def caffe_import(verbose):
    """
    VERBOSE LEVELS
        0 - debug
        1 - info
        2 - warnings
        3 - errors
    :param verbose: int
    :return:
    """
    os.environ['GLOG_minloglevel'] = str(verbose)
    global caffe
    try:
        import caffe
    except ModuleNotFoundError:
        print('CAFFE MODULE NOT FOUND. Suggest: Install caffe-cpu or caffe-cuda')


class LangException(Exception):
    def __init__(self):
        super().__init__("Classifier not available with the inserted language.")


class Classifier(object):
    __slots__ = "net", "transformer", "labels", "verbose", "language"

    def __init__(self, structure_model, pre_trained_model, mean_file, labels_file, verbose='0', language="english"):
        caffe_import(verbose)
        if os.path.splitext(mean_file)[1] == ".binaryproto":
            mean_file = Classifier._protobuf_mean(mean_file)
        self.net, self.transformer = Classifier._build_classifier(structure_model, pre_trained_model, mean_file)
        self.labels = np.genfromtxt(labels_file, delimiter='\t', converters={0: lambda x: x.decode()})
        self.verbose = int(verbose)
        self.language = language

    @staticmethod
    def parse_settings(settings_path, lang="english"):
        with open(settings_path, 'r') as settings_file:
            try:
                settings = json.load(settings_file)[lang]
            except KeyError:
                raise LangException
            structure_model = settings["structure_model"]
            pre_trained_model = settings["pre_trained_model"]
            mean_file = settings["mean_file"]
            labels_file = settings["labels_file"]
            verbose = settings["verbose"]
        return Classifier(structure_model, pre_trained_model, mean_file, labels_file, verbose=verbose, language=lang)

    @staticmethod
    def _build_classifier(structure_model, pretrained_model, mean_file):
        net = caffe.Net(structure_model, pretrained_model, caffe.TEST)
        transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
        transformer.set_mean('data', np.load(mean_file).mean(1).mean(1))
        transformer.set_transpose('data', (2, 0, 1))
        transformer.set_channel_swap('data', (2, 1, 0))
        transformer.set_raw_scale('data', 255.0)
        net.blobs['data'].reshape(10, 3, 224, 224)
        return net, transformer

    @staticmethod
    def _protobuf_mean(protobuf_input, meanfile_output=None):
        if meanfile_output is None:
            meanfile_output = os.path.splitext(protobuf_input)[0] + ".npy"
        blob = caffe.proto.caffe_pb2.BlobProto()
        data = open(protobuf_input, 'rb').read()
        blob.ParseFromString(data)
        # data = np.array(blob.data)
        arr = np.array(caffe.io.blobproto_to_array(blob))
        out = arr[0]
        np.save(meanfile_output, out)
        return meanfile_output

    def set_labels(self, labels_file):
        self.labels = np.genfromtxt(labels_file, delimiter='\t', converters={0: lambda x: x.decode()})

    def get_labels(self):
        return self.labels

    def get_verbose_level(self):
        return self.verbose

    def get_language(self):
        return self.language

    def classify_image(self, image):
        image_labels = None
        im = caffe.io.load_image(image)
        self.net.blobs['data'].data[...] = self.transformer.preprocess('data', im)
        out = self.net.forward()
        image_class_ids = out['prob'].argmax()
        if self.verbose == 0:
            print(image_class_ids)
        top_k = self.net.blobs['prob'].data[0].flatten().argsort()[-1:-6:-1]
        if self.labels is not None:
            image_labels = self.labels[top_k]
            if self.verbose == 0:
                print(image_labels)
        return image_labels if image_labels is not None else []


if __name__ == "__main__":
    language = 'english'
    image_test_dir = '../image_test'
    labels_file_t = "../net/{lang}/{lang}_label.txt".format(lang=language)
    structure_model_proto = '../net/{lang}/{lang}_inception_mvso-hybrid.prototxt'.format(lang=language)
    # or 'english_lr10_iter_210000.prototxt'
    pre_trained_caffemodel = '../net/{lang}/{lang}_inception_mvso-hybrid.caffemodel'.format(lang=language)
    # or 'english_lr10_iter_210000.caffemodel'
    mean_proto = '../net/{lang}/{lang}_meanimage.binaryproto'.format(lang=language)

    # classifier = Classifier(structure_model_proto, pre_trained_caffemodel, mean_proto, labels_file_t, verbose='2')
    classifier = Classifier.parse_settings("../settings/classifier_settings.json", "english")
    for image_t in os.listdir(image_test_dir):
        if image_t.endswith(".jpg"):
            tags = classifier.classify_image(os.path.join(image_test_dir, image_t))
            print("IMAGE : ", image_t)
            print("TAGS : {}".format(" ".join(tags)))
