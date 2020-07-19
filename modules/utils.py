import os
import hashlib
import requests
import json
from itertools import chain
from tqdm import tqdm
from collections import defaultdict
import numpy as np
import ntpath

TRUE = 1
FALSE = 0.5
IND = 0.8


def check_sha1(filename, sha1_hash):
    """Check whether the sha1 hash of the file content matches the expected hash.
    Parameters
    ----------
    filename : str
        Path to the file.
    sha1_hash : str
        Expected sha1 hash in hexadecimal digits.
    Returns
    -------
    bool
        Whether the file content matches the expected hash.
    """
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(1048576)
            if not data:
                break
            sha1.update(data)
    sha1_file = sha1.hexdigest()
    min_len = min(len(sha1_file), len(sha1_hash))
    return sha1.hexdigest()[0:min_len] == sha1_hash[0:min_len]


def download(url, path=None, overwrite=False, sha1_hash=None, reduced_log=False):
    """Download an given URL
    Parameters
    ----------
    url : str
        URL to download
    path : str, optional
        Destination path to store downloaded file. By default stores to the
        current directory with same name as in url.
    overwrite : bool, optional
        Whether to overwrite destination file if already exists.
    sha1_hash : str, optional
        Expected sha1 hash in hexadecimal digits. Will ignore existing file when hash is specified
        but doesn't match.
    reduced_log : str, optional
        If True only basename of the file will be printed instead of the entire relative path.
    Returns
    -------
    str
        The file path of the downloaded file.
    """
    if path is None:
        fname = url.split('/')[-1]
    else:
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            fname = os.path.join(path, url.split('/')[-1])
        else:
            fname = path

    if overwrite or not os.path.exists(fname) or (sha1_hash and not check_sha1(fname, sha1_hash)):
        dirname = os.path.dirname(os.path.abspath(os.path.expanduser(fname)))
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        if reduced_log:
            print('Downloading %s...' % (ntpath.basename(fname)))
        else:
            print('Downloading %s from %s...' % (fname, url))
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            raise RuntimeError("Failed downloading url %s" % url)
        total_length = r.headers.get('content-length')
        with open(fname, 'wb') as f:
            if total_length is None:  # no content length header
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            else:
                total_length = int(total_length)
                for chunk in tqdm(r.iter_content(chunk_size=1024),
                                  total=int(total_length / 1024. + 0.5),
                                  unit='KB', unit_scale=False, dynamic_ncols=True):
                    f.write(chunk)

        if sha1_hash and not check_sha1(fname, sha1_hash):
            raise UserWarning('File {} is downloaded but the content hash does not match. '
                              'The repo may be outdated or download may be incomplete. '
                              'If the "repo_url" is overridden, consider switching to '
                              'the default repo.'.format(fname))
    elif not overwrite and os.path.exists(fname):
        print('Reading %s from cache...' % (ntpath.basename(fname) if reduced_log else fname))
    return fname


def download_file(url, directory, file_name=None, overwrite=False, reduced_log=False):
    """
    Download file in specified path.
    :param url: str
    :param directory: str
    :param file_name: str
    :param overwrite: bool
    :param reduced_log: bool
    :return:
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    if file_name is not None:
        directory = os.path.join(directory, file_name)
    return download(url, path=directory, overwrite=overwrite, reduced_log=reduced_log)


def remove_file(filename):
    os.remove(filename)


def reliability_score(truth_labels, tags_in_onto, tags_out_onto, percent=True):
    """
    :param percent: bool
    :param truth_labels: set
    :param tags_in_onto: set
    :param tags_out_onto: set
    :return: float
    """
    truth_labels = set(truth_labels)
    # truth_not_tagged = len(truth_labels - tags_in_onto)
    true_onto_tags = len(truth_labels & tags_in_onto)
    false_onto_tags = len(tags_in_onto - truth_labels)
    indefinable = len(tags_out_onto)
    score = np.around((TRUE * true_onto_tags + FALSE * false_onto_tags + IND * indefinable) / (
            true_onto_tags + false_onto_tags + indefinable), 3)
    return percentage(score, 1) if percent else score


def serialize_results(data, file_name):
    with open(file_name, 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)


def get_phrases(fle):
    phrase_dict = defaultdict(list)
    with open(fle) as ph:
        for line in map(str.rstrip, ph):
            k, _, phr = line.partition(" ")
            phrase_dict[k].append(line)
        return phrase_dict


def replace(fle, dct):
    with open(fle) as f:
        for line in f:
            phrases = sorted(chain.from_iterable(dct[word] for word in line.split() if word in dct), reverse=True,
                             key=len)
            for phr in phrases:
                line = line.replace(phr, phr.replace(" ", "_"))
            yield line


def average(cls, tmp_default_list):
    return {tmp_key: np.around(sum(s_list) / len(s_list), 3) for tmp_key, s_list in tmp_default_list.items()}


def percentage(val, max_val, integer=True, absolute=False):
    percentage_val = 100 * float(val) / float(max_val)
    percentage_val = int(percentage_val) if integer else np.around(percentage_val, 1)
    return abs(percentage_val) if absolute else percentage_val
