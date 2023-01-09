import os
from werkzeug.utils import secure_filename
import uuid as uuid

from config import Config


def examination_message(mes):
    tags = list()
    message = list()
    for word in mes.split():
        if '#' in word:
            tags.append(word.replace('#', ''))
        else:
            message.append(word)
    message = ' '.join(message)
    return message, tags


def avatar_saver(photo):
    photo_name = str(uuid.uuid1())
    photo.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), Config.UPLOAD_FOLDER, photo_name))


def photo_saver(photos):
    photos_name = list()
    for photo in photos:
        photo_name = str(uuid.uuid1())
        photo.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), Config.UPLOAD_FOLDER, photo_name))
        photos_name.append(photo_name)
    return photos_name