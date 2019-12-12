from django.db import models
from django.conf import settings
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
# from django.core.validators import *
import re
from datetime import datetime
from django.utils import timezone

from io import BytesIO
from django.core.files.base import ContentFile
import os
import time
from django.core.files.uploadedfile import SimpleUploadedFile
import hashlib
import PIL
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
from datetime import datetime
from django.core.files import File
import pytz
import logging
import cv2
import numpy as np

# Image thumbnail processing

# Create your models here.

# What do I want to happen when the images have the same hash? 
# What if the image changes? 
# What if the image moves? 
# -- Update the record.

# print(settings.LOG_LEVEL)
# logging.basicConfig(filename=settings.LOG_FILE, level=settings.LOG_LEVEL)


# logging.basicConfig(filename='example.log',level=logging.DEBUG)
settings.LOGGER.warning("TODO: Need to handle thumbnails in this better")
settings.LOGGER.warning("TODO: May want to handle bad files more gracefully.")
settings.LOGGER.warning("TODO: More logic is needed to see if the file has changed at all, instead of just hash")

# Latitude and longitude validators that accomodate out-of-GPS coordinates for
# default "not there" values.
def validate_lat(value):
    if value != -999:
        if not -90 < value < 90:
            raise ValidationError(
                _('%(value)s is not a valid latitude'),
                params={'value': value},
            )

def validate_lon(value):
    if value != -999:
        if not -180 < value < 180:
            raise ValidationError(
                _('%(value)s is not a valid latitude'),
                params={'value': value},
            )

class Directory(models.Model): 
    dir_path = models.CharField(max_length=255, unique=True)
    mean_datetime = models.DateTimeField(default = timezone.now)
    mean_datesec = models.FloatField(default = -1)
    first_datetime = models.DateTimeField(default = timezone.now)
    first_datesec = models.FloatField(default = -1)

    def __str__(self):
        return "{} --- ({})".format(self.dir_path.split('/')[-1], self.dir_path)

    def top_level_name(self):
        return "{}".format(self.dir_path.split('/')[-1])

    def imgs_in_dir(self):
        imgs = ImageFile.objects.filter(directory__dir_path=self.dir_path)
        imgs = [i.id for i in imgs]
        return imgs

    def __get_filtered_img_dates__(self):
        imgs = ImageFile.objects.filter(directory__dir_path=self.dir_path)

        img_date = [time.mktime(i.dateTaken.timetuple()) for i in imgs if i.dateTakenValid]
        img_date = np.array(img_date)

        def reject_outliers(data, m = 2.):
            d = np.abs(data - np.median(data))
            mdev = np.median(d)
            s = d/mdev if mdev else 0.
            return data[s<m]

        img_date =reject_outliers(img_date)
        if len(img_date) == 0:
            return None
        else:
            return img_date.reshape(-1)

    def average_date_taken(self):
        img_dates = self.__get_filtered_img_dates__()
        if img_dates is None:
            self.mean_datesec = datetime.fromtimestamp(timezone.now, timezone.utc)
            self.mean_datetime = datetime.fromtimestamp(self.mean_datesec, timezone.utc)
        else:
            self.mean_datesec = float(np.mean(img_dates))
            self.mean_datetime = datetime.fromtimestamp(self.mean_datesec, timezone.utc)

    def beginning_date_taken(self):
        img_dates = self.__get_filtered_img_dates__()
        if img_dates is None:
            self.first_datesec = datetime.fromtimestamp(timezone.now, timezone.utc)
            self.first_datetime = datetime.fromtimestamp(self.mean_datesec, timezone.utc)
        else:
            img_dates.sort()
            first_date = img_dates[0]
            self.first_datesec = int(first_date)
            self.first_datetime = datetime.fromtimestamp(self.first_datesec, timezone.utc)
    
# Lots ripped from https://github.com/hooram/ownphotos/blob/dev/api/models.py 
class ImageFile(models.Model):

    filename = models.CharField(max_length=255, validators=[RegexValidator(regex="\.[j|J][p|P][e|E]?[g|G]$", message="Filename must be a JPG")], db_index = True)
    # CASCADE is expected; if delete directory, delete images.
    directory = models.ForeignKey(Directory, on_delete=models.PROTECT)
    pixel_hash = models.CharField(max_length = 64, null = False, default = -1)
    file_hash = models.CharField(max_length = 64, null = False, default = -1)

    # Thumbnails 
    thumbnail_big = models.ImageField(upload_to='thumbnails_big', editable=False, default=None)
    thumbnail_medium = models.ImageField(upload_to='thumbnails_med', editable=False, default=None)
    thumbnail_small = models.ImageField(upload_to='thumbnails_small', editable=False, default=None)

    # square_thumbnail = models.ImageField(upload_to='square_thumbnails')
    # square_thumbnail_tiny = models.ImageField(
    #     upload_to='square_thumbnails_tiny')
    # square_thumbnail_small = models.ImageField(
    #     upload_to='square_thumbnails_small')
    # square_thumbnail_big = models.ImageField(upload_to='square_thumbnails_big')

    # Fields for metadata
    camera_make = models.CharField(max_length = 64, null=True, blank=True)
    camera_model = models.CharField(max_length = 64, null=True, blank=True)
    flash_info = models.IntegerField(validators=[MinValueValidator(-1)], default= -1)
    exposure_num = models.IntegerField(validators=[MinValueValidator(-1)], default= -1)
    exposure_denom = models.IntegerField(validators=[MinValueValidator(-1)], default= -1)
    focal_num = models.IntegerField(validators=[MinValueValidator(-1)], default= -1)
    focal_denom = models.IntegerField(validators=[MinValueValidator(-1)], default= -1)
    fnumber_num = models.IntegerField(validators=[MinValueValidator(-1)], default= -1)
    fnumber_denom = models.IntegerField(validators=[MinValueValidator(-1)], default= -1)
    iso_value = models.IntegerField(validators=[MinValueValidator(-1)], default= -1)
    light_source = models.IntegerField(validators=[MinValueValidator(-1)], default= -1)
    gps_lat_decimal = models.FloatField(default=-999,validators=[validate_lat])
    gps_lon_decimal = models.FloatField(default=-999,validators=[validate_lon])

    # Default for date added is now.
    dateAdded = models.DateTimeField( default=timezone.now )
    dateModified = models.DateTimeField(default = timezone.now )
    width = models.IntegerField(validators=[MinValueValidator(1)])
    height = models.IntegerField(validators=[MinValueValidator(1)])

    # Default for date take in January 1, 1899.
    dateTaken = models.DateTimeField( default=datetime(2018, 1, 1) )
    dateTakenValid = models.BooleanField(default=False)

    # isProcessed -- whether the photo has had faces detected.
    isProcessed = models.BooleanField(default=False)
    orientation = models.IntegerField(default=-8008)

    # thumbnail = models.ImageField(upload_to = settings.FILEPOPULATOR_THUMBNAIL_DIR, default = str(timezone.now) + '_thumbnail.jpg' )

    # def _get_full_path(self):
    #     expand_dir = self.directory.dir_path
    #     fullname = os.path.join(expand_dir, self.filename)
    #     return fullname


    def __str__(self):
        return "{}".format(self.filename)

    def process_new_no_md5(self):

        is_new = True

        if not re.match(".*\.[j|J][p|P][e|E]?[g|G]$", self.filename):
            settings.LOGGER.debug("File {} does not have a jpeg-type ending.".format(self.filename))
            return False # Success value

        self._init_image()
        self._get_dir()
        s = time.time()
        self._get_date_taken()

        return True # Success value

        # name_match = ImageFile.objects.filter(filename=self.filename)
        # if name_match: # i.e. we've looked at this file before.
        #     is_new = False
        #     assert len(name_match) == 1, 'More than one record for same image filepath.'
        #     old_pixel_hash = name_match[0].pixel_hash
        #     if old_pixel_hash == self.pixel_hash:
        #         # Still the same picture. We're good.
        #         return
        #     else:
        #         settings.LOGGER.debug("TODO: File repeat with changes. Need logic to see if the file has changed at all...")
                # raise NotImplementedError('What do we do here?')
            # return


        # self._generate_thumbnail()

        # hash_match = ImageFile.objects.filter(pixel_hash__contains=self.pixel_hash)
        # if hash_match and name_match:
        #     raise NotImplementedError('Hashes match! Need better info...')
        #     return
            # Do some other checks. Do the filenames match?
            # return
        # match = ImageFile.objects.filter(filename__contains=self.filename)# .get(image_hash = self.image_hash))
        # print(match.values('image_hash'))


    def _get_dir(self):
        directory_of_file = os.path.dirname( os.path.normpath( self.filename ) )

        try:
            self.directory = Directory.objects.get (dir_path = directory_of_file)
        except :
            instance = Directory(dir_path = directory_of_file)
            try:
                instance.full_clean()
            except ValidationError as ve:
                print(ve)
            else:
                instance.save()

            self.directory = Directory.objects.get(dir_path = directory_of_file)

    def _init_image(self):
        # # Get the date taken:
        # # Source for these EXIF tag attributes: 
        # # https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif.html
        # # exifDict = {}
        # # exifDict['DateTimeOriginal'] key = 36867
        # # exifDict['DateTimeDigitized'] key = 36868
        
        # # Source for this code snippet: 
        # # https://www.blog.pythonlibrary.org/2010/03/28/getting-photo-metadata-exif-using-python/
        # # Uses PIL to get a named dictionary of EXIF metadata.


        s = time.time()
        self.image = PIL.Image.open(self.filename)
        self.dateModified = datetime.fromtimestamp(os.path.getmtime(self.filename))
        if self.dateModified.tzinfo == None:
            self.dateModified = self.dateModified.astimezone(pytz.utc)


        self.exifDict = {}
        # print(self.filename)
        try:
            info = self.image._getexif()
        except AttributeError as ae:
            info = None
        if info is not None:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                self.exifDict[decoded] = value
        else:
            self.orientation = 1
            self.exifDict = None

        if 'keys' in dir(self.exifDict):
            tags = ['Make', 'Model', 'Flash', 'ExposureTime', 'FocalLength', 'ISOSpeedRatings', 'FNumber', 'LightSource']

            if 'GPSInfo' in self.exifDict.keys():

                for key in self.exifDict['GPSInfo'].keys():
                    name = GPSTAGS.get(key,key)
                    self.exifDict['GPSInfo'][name] = self.exifDict['GPSInfo'].pop(key)
                # For *whatever* reason, some of the keys don't convert on the first pass.
                for key in self.exifDict['GPSInfo'].keys():
                    name = GPSTAGS.get(key,key)
                    self.exifDict['GPSInfo'][name] = self.exifDict['GPSInfo'].pop(key)

                def get_decimal_coordinates(info):
                    
                    for key in ['Latitude', 'Longitude']:
                        if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
                            e = info['GPS'+key]
                            ref = info['GPS'+key+'Ref']
                            info[key] = ( e[0][0]/e[0][1] +
                                          e[1][0]/e[1][1] / 60 +
                                          e[2][0]/e[2][1] / 3600
                                        ) * (-1 if ref in ['S','W'] else 1)

                    if 'Latitude' in info and 'Longitude' in info:
                        # print(info)
                        return [info['Latitude'], info['Longitude']]
                    else:
                        return [-999, -999]

                gps_lat, gps_lon = get_decimal_coordinates(self.exifDict['GPSInfo'])
                self.exifDict['GPSInfo']['GPSLatDec'] = gps_lat
                self.exifDict['GPSInfo']['GPSLonDec'] = gps_lon


            # We can - and should - decode the flash and light source 
            # values elsewhere, rather than putting that logic here. Plus 
            # I'm not feeling it right now. 
            if 'Make' in self.exifDict.keys():
                make = self.exifDict['Make']
                self.camera_make = make
            if 'Model' in self.exifDict.keys():
                model = self.exifDict['Model']
                self.camera_model = model
            if 'Flash' in self.exifDict.keys():
                flash = self.exifDict['Flash']
                self.flash_info = flash
            if 'ExposureTime' in self.exifDict.keys():
                exposureTime = self.exifDict['ExposureTime']
                self.exposure_num = exposureTime[0]
                self.exposure_denom = exposureTime[1]
            if 'FocalLength' in self.exifDict.keys():
                focalLength = self.exifDict['FocalLength']
                self.focal_num = focalLength[0]
                self.focal_denom = focalLength[1]
            if 'ISOSpeedRatings' in self.exifDict.keys():
                iso = self.exifDict['ISOSpeedRatings']
                self.iso_value = iso
            if 'FNumber' in self.exifDict.keys():
                fnumber = self.exifDict['FNumber']
                self.fnumber_num = fnumber[0]
                self.fnumber_denom = fnumber[1]
            if 'LightSource' in self.exifDict.keys():
                light_source = self.exifDict['LightSource']
                self.light_source = light_source
            if 'GPSInfo' in self.exifDict.keys():
                self.gps_lat_decimal = self.exifDict['GPSInfo']['GPSLatDec']
                self.gps_lon_decimal = self.exifDict['GPSInfo']['GPSLonDec']
            if 'Orientation' in self.exifDict.keys():
                self.orientation = self.exifDict['Orientation']
            else:
                self.orientation = 1

        self.dateAdded = timezone.now()


        # If no ExifTags, no rotating needed.
        try:
            # Grab orientation value.
            # Already done in _init_image()

            # Rotate depending on orientation.
            if self.orientation == 2:
                self.image = self.image.transpose(PIL.Image.FLIP_LEFT_RIGHT)
            if self.orientation == 3:
                self.image = self.image.transpose(PIL.Image.ROTATE_180)
            if self.orientation == 4:
                self.image = self.image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
            if self.orientation == 5:
                self.image = self.image.transpose(PIL.Image.FLIP_LEFT_RIGHT).transpose(
                    PIL.Image.ROTATE_90)
            if self.orientation == 6:
                self.image = self.image.transpose(PIL.Image.ROTATE_270)
            if self.orientation == 7:
                self.image = self.image.transpose(PIL.Image.FLIP_TOP_BOTTOM).transpose(
                    PIL.Image.ROTATE_90)
            if self.orientation == 8:
                self.image = self.image.transpose(PIL.Image.ROTATE_90)
        except:
            # Orientation 1 
            pass

        self.width, self.height = self.image.size

    # Orientation ? 
    def _generate_md5_hash(self):
        # Reads the pixels in the image, reshapes them,
        # and then hash the pixels one by one using md5. 
        pixel_hash_md5 = hashlib.md5()

        self.pixels = cv2.cvtColor(np.array(self.image), cv2.COLOR_BGR2RGB)

        arr = self.pixels.reshape(-1)
        # arr = arr[::500]
        # arr = np.ascontiguousarray(arr)
        # print(arr)

        # Sample 1000 pixels in the array equally across the array.
        # This is deterministic. 
        # for idx in range(0,len(arr),max(len(arr)//1000, 1) ):
        #     it = arr[idx]
        #     pixel_hash_md5.update(bytes([it]))
        pixel_hash_md5.update(arr)
        
        self.pixel_hash = pixel_hash_md5.hexdigest()
        settings.LOGGER.debug(f'{self.pixel_hash}, {self.filename}')

        hash_file = hashlib.md5()
        # with open(self.filename, "rb") as f:
        #     for chunk in iter(lambda: f.read(4096), b""):
        #         hash_file.update(chunk)
        hash_file.update(self.filename.encode('utf-8'))
        self.file_hash = hash_file.hexdigest() 

        # Look for other files with same hashes
        other_hashed = ImageFile.objects.filter(pixel_hash = self.pixel_hash)
        if len(other_hashed):
            for obj in other_hashed:
                if os.path.exists(obj.filename):
                    pass
                    settings.LOGGER.debug("Assumption made about same pixel hash and existing file, but not same filename: do nothing.")
                   #  raise NotImplementedError('Same object hash -- what to do?')
                else:
                    pass
                    # Do nothing
                    settings.LOGGER.debug('Same hash as a deleted item. Watch this.')
                    # obj.thumbnail.delete()
                    # obj.delete()

    def _get_date_taken(self):
        # Default comparison date - we want the earliest date.
        self.dateTaken = timezone.now()
        # Flag for if we found a date taken in the EXIF data. 
        self.dateTakenValid = False

        if self.exifDict is not None:
            dateTakenKeys = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
            for exifKey in dateTakenKeys:
                datetaken_tmp = self.exifDict[exifKey] if exifKey in self.exifDict.keys() else None
                if datetaken_tmp is None:
                    continue  # No value at this EXIF key
                else:
                    date = datetime.strptime(datetaken_tmp, '%Y:%m:%d %H:%M:%S')
                    date = pytz.utc.localize(date)
                    if date < self.dateTaken: 
                        self.dateTaken = date
                        self.dateTakenValid = True
        else:
            self.dateTaken = timezone.now()
            self.dateTakenValid = False
            settings.LOGGER.warning(f"Date taken is not valid for file {self.filename}")

        # settings.LOGGER.error('Hi, debug here:')

        # Make the taken date timezone aware to get rid of warnings.
        # self.dateTaken = (self.dateTaken)

    def _generate_thumbnail(self):
        """
        Create and save the thumbnail for the photo (simple resize with PIL).
        """
        # fh = storage.open(self.photo_name, 'r')
        # try:
        #     image = Image.open(self.filename)
        # except:
        #     print("Couldn't open")  
        #     return False

        thumb_fields = [self.thumbnail_big, self.thumbnail_medium, self.thumbnail_small]
        thumb_sizes = [settings.FILEPOPULATOR_THUMBNAIL_SIZE_BIG, \
                        settings.FILEPOPULATOR_THUMBNAIL_SIZE_MEDIUM, \
                        settings.FILEPOPULATOR_THUMBNAIL_SIZE_SMALL]

        for field, size in zip(thumb_fields, thumb_sizes):


            image = self.image

            image.thumbnail(size, Image.ANTIALIAS)

            thumb_filename = f'{self.pixel_hash}_{self.file_hash}.jpg'

            FTYPE = 'JPEG' # 'GIF' or 'PNG' are possible extensions

            # Save thumbnail to in-memory file as StringIO
            temp_thumb = BytesIO()
            image.save(temp_thumb, FTYPE)
            temp_thumb.seek(0)

            # Load a ContentFile into the thumbnail field so it gets saved
            field.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)

            temp_thumb.close()

        return True

    def save(self, *args, **kwargs):
        """
        Make and save the thumbnail for the photo here.
        """
        # I only do the MD5 hash in the save function because it
        # is so expensive. I also have to redo the _init_image function
        # for some reason, so that the self.image field is populated
        # appropriately (it somehow loses it...)

        self._init_image()
        self._generate_md5_hash()

        if not self._generate_thumbnail():
            raise Exception('Could not create thumbnail - is the file type valid?')
        super(ImageFile, self).save(*args, **kwargs)

    def delete(self):
        # file = ImageFile.objects.filter(id=self.id)
        # os.remove(file[0].thumbnail_small.path)
        os.remove(self.thumbnail_big.path)
        os.remove(self.thumbnail_medium.path)
        os.remove(self.thumbnail_small.path)
        super(ImageFile, self).delete()


    # def admin_thumbnail(self):
    #         func = getattr(self, 'get_admin_thumbnail_url', None)
    #         if func is None:
    #             return _('An "admin_thumbnail" photo size has not been defined.')
    #         else:
    #             if hasattr(self, 'get_absolute_url'):
    #                 return mark_safe(u'<a href="{}"><img src="{}"></a>'.format(self.get_absolute_url(), func()))
    #             else:
    #                 return mark_safe(u'<a href="{}"><img src="{}"></a>'.format(self.image.url, func()))

    # admin_thumbnail.short_description = ('Thumbnail')
    # admin_thumbnail.allow_tags = True
    def image_img(self):
        if self.image:
            return marksafe('<img src="%s" />' % self.thumbnail_small.url)
        else:
            return '(Sin imagen)'
        image_img.short_description = 'Thumb'


    def exposure(self):
        return f"{self.exposure_num}/{self.exposure_denom}"
        
    exposure.short_description = 'Exposure'
