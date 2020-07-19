import flickrapi
import os
import json
import urllib.parse
from modules import utils


class Photo:
    __slots__ = "identifier", "link", "download_link", "title", "tags"

    def __init__(self, identifier, title, base_link, owner_id):
        self.identifier = identifier
        self.title = title
        self.link = urllib.parse.urljoin(urllib.parse.urljoin(base_link, owner_id) + "/", self.identifier)
        self.download_link = ""
        self.tags = list()

    def set_download_link(self, farm, server, secret, image_size):
        download_template = "https://farm{0}.staticflickr.com/{1}/{2}_{3}{4}.jpg"
        self.download_link = download_template.format(farm, server, self.identifier, secret, image_size)

    def add_tags(self, tag):
        self.tags.append(tag)

    def structured_data(self):
        return {
            self.identifier: {
                "title": self.title,
                "link": self.link,
                "download_link": self.download_link,
                "tags": self.tags
            }
        }


class FlickrSet:
    __slots__ = "flickr", "flickr_image_sizes", "image_size", "base_link", "temp_directory"

    def __init__(self, conf_file_path, temp_directory="image_cache", image_size="default"):
        with open(conf_file_path, 'r') as conf_file:
            conf = json.load(conf_file)
        self.flickr = flickrapi.FlickrAPI(conf['my_api_key'], conf['my_api_secret'], cache=True, format='parsed-json')
        self.flickr_image_sizes = conf['image_sizes']
        self.image_size = self.set_image_size(image_size)
        self.base_link = conf['base_link']
        self.temp_directory = temp_directory

    def set_image_size(self, image_size):
        return self.flickr_image_sizes[image_size]

    def get_image_size(self):
        return self.image_size

    def get_data_from_name(self, user_name):
        found_user_id = self.get_user_id(user_name)
        return found_user_id, self.get_data_from_id(found_user_id)

    def get_user_id(self, user_name):
        return self.flickr.people.findByUsername(username=user_name)["user"]["id"]

    def get_user_pic_link(self, user_id):
        download_format_pic = "http://farm{}.staticflickr.com/{}/buddyicons/{}_r.jpg"
        info = self.flickr.people.getInfo(user_id=user_id)["person"]
        return download_format_pic.format(info["iconfarm"], info["iconserver"], info["nsid"])

    def get_user_name(self, user_id):
        return self.flickr.people.getInfo(user_id=user_id)["person"]["username"]["_content"]

    def get_image_from_tags(self, tags):
        page = 1
        while True:
            data = self.flickr.photos.search(tags=list(tags), tag_mode="all", per_page=1, page=page)
            if page > data["photos"]["pages"]:
                break
            photo_id = data["photos"]["photo"][0]["id"]
            photo_title = data["photos"]["photo"][0]["title"]
            photo_owner_id = data["photos"]["photo"][0]["owner"]
            farm = data["photos"]["photo"][0]["farm"]
            server = data["photos"]["photo"][0]["server"]
            secret = data["photos"]["photo"][0]["secret"]
            photo = Photo(photo_id, photo_title, self.base_link, photo_owner_id)
            photo.set_download_link(farm, server, secret, self.image_size)
            for tag in self.flickr.photos.getInfo(photo_id=photo_id)['photo']['tags']['tag']:
                photo.add_tags(tag['raw'])
            yield photo_id, photo.structured_data()[photo_id]
            page += 1

    def get_data_from_id(self, owner_id):
        """
        :param owner_id: string
        :return: dict
        { "433546289" : {
             title  :  DSCF0995
             link  :  https://www.flickr.com/photos/7488735@N03/433546289
             download_link  :  https://farm1.staticflickr.com/152/433546289_0b8b8d3aaf.jpg
             tags  :  ['puppy', 'pet', 'dog', 'cat']
            }
        }
        """
        data_dict = dict()
        f_photos = self.flickr.people.getPhotos(user_id=owner_id)
        for f_photo in f_photos['photos']['photo']:
            photo_id = f_photo['id']
            photo = Photo(photo_id, f_photo['title'], self.base_link, owner_id)
            photo.set_download_link(f_photo['farm'], f_photo['server'], f_photo['secret'], self.image_size)
            for tag in self.flickr.photos.getInfo(photo_id=photo_id)['photo']['tags']['tag']:
                photo.add_tags(tag['raw'])
            data_dict.update(photo.structured_data())
        return data_dict

    def set_temp_directory(self, temp_directory):
        self.temp_directory = temp_directory

    def get_temp_directory(self):
        return self.temp_directory

    def download_images(self, image_dictionary):
        for _, data_dict in image_dictionary.items():
            utils.download_file(data_dict['download_link'], self.temp_directory)

    def download_all_images(self, owner_id):
        self.download_images(self.get_data_from_id(owner_id=owner_id))

    def remove_temp_images(self):
        for the_file in os.listdir(self.temp_directory):
            file_path = os.path.join(self.temp_directory, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    user_id_test = "7488735@N03"
    flickr_settings = "../settings/flickr_settings.json"
    flickr = FlickrSet(flickr_settings)
    print(flickr.get_user_pic_link(flickr.get_user_id("giant_schnauzer")))
    input()
    print(flickr.get_user_name(user_id_test))
    for photo_structure in flickr.get_image_from_tags(["moon"]):
        print(photo_structure)
        input("PRESS ANY KEY TO CONTINUE...")
    data = flickr.get_data_from_id(user_id_test)
    for image_id, information in data.items():
        print(image_id)
        for info_key, info_value in information.items():
            print("\t", info_key, " : ", info_value)
    flickr.download_images(data)
    input("PRESS ANY KEY TO CONTINUE...")
    flickr.remove_temp_images()
