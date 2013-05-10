from database import *
import time as _time
import datetime

class Photo(object):
	pass
class ExifData(object):
	def __init__(self):
		self.camera = ''
		self.exposure = ''
		self.aperture = ''
		self.focal_length = ''
		self.iso_speed = ''
		self.lens = ''

class IrEtl:
	def __init__(self, connection):
		self.connection = connection
		self.toSave = []
	
	def etl(self, photo, exif, comments):
		t = self.transform(photo, exif, comments)
		self.toSave.append(t)
		return t

	def commit(self):
		etlInsertPhoto(self.connection, self.toSave)
		self.toSave = []

	def transform(self, photo, exif, comments):
		sanph = Photo()
		sanph.id = photo['id']
		sanph.owner = photo['owner']

		prefixes = 'o', 'b', 'c', 'z', 'n', 'm', 't', 'q', 's'

		# image url
		for prefix in prefixes:
			if 'url_' + prefix in photo:
				sanph.url = photo['url_' + prefix]
				break

		# thumbnail
		for prefix in reversed(prefixes):
			if 'url_' + prefix in photo:
				sanph.thumbnail = photo['url_' + prefix]
				break

		# width
		for prefix in prefixes:
			if 'width_' + prefix in photo:
				sanph.width = photo['width_' + prefix]
				break
		
		# height
		for prefix in prefixes:
			if 'height_' + prefix in photo:
				sanph.height = photo['height_' + prefix]
				break
		
		#others
		sanph.license = photo['license']
		if 'latitude' in photo:
			sanph.latitude = photo['latitude']
		if 'longitude' in photo:
			sanph.longitude = photo['longitude']
		if 'machine_tags' in photo:
			sanph.machine_tags = photo['machine_tags']
		sanph.views = photo['views']
		sanph.description = photo['description']['_content']
		sanph.dateupload = convertFromPosix(photo['dateupload'])
		if 'lastupdate' in photo:
			sanph.last_update = convertFromPosix(photo['lastupdate'])
		else:
			sanph.last_update = ''
		sanph.title = photo['title']
		p = None
		try:
			p = datetime.datetime.strptime(photo['datetaken'],'%Y-%m-%d %H:%M:%S')
		except Exception as e:
			pass
		sanph.datetaken = p
		sanph.ownername = photo['ownername']
		if 'pathalias' in photo and photo['pathalias'] != None:
			sanph.pathalias = photo['pathalias']
		else:
			sanph.pathalias = ''
		sanph.tags = photo['tags']
		sanph.comments = self.joinComments(comments)

		# Exif Data
		exifObject = self.extractExifData(exif)
		sanph.camera = exifObject.camera
		sanph.exposure = exifObject.exposure
		sanph.aperture = exifObject.aperture
		sanph.focal_length = exifObject.focal_length
		sanph.iso_speed = exifObject.iso_speed
		sanph.lens = exifObject.lens;
		return sanph

	def joinComments(self, comments):
		longComment = ''
		if 'comment' in comments['comments']:
			for single in comments['comments']['comment']:
				longComment += single['_content'] + '\n'
		return longComment
	def extractExifData(self, exifEntity):
		result = ExifData()
		if exifEntity is not None and 'photo' in exifEntity:
			if 'camera' in exifEntity['photo']:
				result.camera = exifEntity['photo']['camera']
			for item in exifEntity['photo']['exif']:
				if 'Exposure' == item['label']:
					result.exposure = item['raw']['_content']
				elif 'Aperture' in item['label']:
					result.aperture = item['raw']['_content']
				elif 'Focal Length' in item['label']:
					result.focal_length = item['raw']['_content']
				elif 'ISO' in item['label']:
					result.iso_speed = item['raw']['_content']
				elif 'Lens' == item['label'] or 'Lens Model' == item['label']:
					result.lens = item['raw']['_content']
		return result