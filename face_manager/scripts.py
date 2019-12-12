
from django.conf import settings

from filepopulator.models import ImageFile
from .models import Person, Face
import image_face_extractor
import cv2
from io import BytesIO
from django.core.files.base import ContentFile
import numpy as np
import logging

def populateFromImage(filename):

    settings.LOGGER.error("Need better handling on foreign_key")
    foreign_key = ImageFile.objects.get(filename = filename)
    print(foreign_key.isProcessed)
    if foreign_key.isProcessed:
        return None

    # def face_from_facerect(self, filename):
    face_data = image_face_extractor.image_client.face_extract_client(filename)

    assert len(foreign_key) == 1
    foreign_key = foreign_key[0]

    if len(face_data) == 0:
        foreign_key.isProcessed = True
        foreign_key.save()
        return None
    # implied else


    for idx in range(len(face_data)):
        eachface = face_data[idx]
        name = eachface.name
        encoding = list(eachface.encoding)
        square_face = eachface.square_face
        rect = eachface.rectangle
        r_left = rect.left
        r_right = rect.right
        r_bot = rect.bottom
        r_top = rect.top

        new_face = Face()

        if name is not None:
            # Find the person, if possible
            person_key = Person.objects.filter(person_name = name)
            if len(person_key) == 0:
                new_person = Person(person_name = name)
                new_person.save()
                person_key = Person.objects.filter(person_name = name)
                assert len(person_key) == 1
                new_face.written_to_photo_metadata = False
            else:
                new_face.written_to_photo_metadata = True

            person_key = person_key[0]

            new_face.declared_name = person_key

        if encoding is not None:
            new_face.face_encoding = encoding

        new_face.box_top = r_top
        new_face.box_bottom = r_bot
        new_face.box_left = r_left
        new_face.box_right = r_right

        # new_face.face_thumbnail = square_face
        # Save the thumbnail
        sq_thumb = np.flip(square_face, 2) # BGR to RGB
        # sq_thumb = np.cv2.cvtColor(sq_thumb, cv2.COLOR_BGR2RGB)
        thumb_filename = f'{foreign_key.pixel_hash}_{foreign_key.file_hash}_face{idx}.jpg'

        FTYPE = 'JPEG' # 'GIF' or 'PNG' are possible extensions

        # Save thumbnail to in-memory file as StringIO

        # encode
        is_success, buffer_img = cv2.imencode(".jpg", sq_thumb)
        temp_thumb = BytesIO(buffer_img)
        # temp_thumb = BytesIO()
        # cv2.imwrite(temp_thumb, sq_thumb)
        # image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # Load a ContentFile into the thumbnail field so it gets saved
        new_face.face_thumbnail.save(thumb_filename, ContentFile(temp_thumb.read())) #, save=False)

        temp_thumb.close()

        new_face.save()


    return face_data