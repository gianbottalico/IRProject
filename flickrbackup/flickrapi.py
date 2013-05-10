import requests, json, copy, hashlib
from secret import api_key
from utils import *
import database

class FlickrResponse:
	def __init__(self, method, params, main_arg, response):
		self.method   = method
		self.params   = params
		self.main_arg = main_arg
		self.result = response
		self.cached = False
	def digest(self):
		p = copy.deepcopy(self.params)
		p['method'] = self.method
		if 'api_key' in p: del p['api_key']
		if 'format' in p: del p['format']
		if 'per_page' in p: del p['per_page']

		# Compute the hash
		m = hashlib.sha1()
		m.update(self.method.encode('utf-8'))
		m.update(json.dumps(sorted(p.items(), key=lambda x: x[0])).encode('utf-8'))
		return m.hexdigest()

	def loadFromCache(self, db):
		r = database.getCachedResultsFor(db, self.digest())
		if r != None:
			self.cached = True
			self.result = r
			return True
		return False

def callFlickrAPI(db, method, options = {}, main_arg=''):
	result = FlickrResponse(method, options, main_arg, None)
	if result.loadFromCache(db):
		return result

	params = mergeDicts({
			'method': method,
			'api_key': api_key,
			'format': 'json',
			'per_page': 500,
		}, options)

	r = requests.get('http://api.flickr.com/services/rest', params=params)
	r = r.text

	# Remove the first 'jsonFlickrApi(', and the last ')'
	result.result = json.loads(r[14:-1])
	return result

def getPhotosOf(db, userid, maxpages=9999):
	logMessage('flickr', 'Getting photos of %s' % (userid))

	result = FlickrResponse('flickr.people.getPublicPhotos',
		{'user_id': userid, 'extras': 'description, license, date_upload, date_taken, owner_name, icon_server, original_format, last_update, geo, tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o'},
		userid, None)
	if result.loadFromCache(db):
		return result

	photos = []
	totalPages = 1
	currentPage = 0
	apiResponse = None

	while(currentPage < totalPages):
		options = {
			'user_id': userid,
			'page': (currentPage+1),
			'extras': 'description, license, date_upload, date_taken, owner_name, icon_server, original_format, last_update, geo, tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o'
		}

		apiResponse = callFlickrAPI(db, 'flickr.people.getPublicPhotos', options)
		qres = apiResponse.result

		currentPage = qres['photos']['page']
		totalPages = qres['photos']['pages']
		if totalPages > maxpages:
			totalPages = maxpages

		for photo in qres['photos']['photo']:
			photos.append(photo)

		logMessage('flickr', ' > Got page %i out of %i (%i photos)' % (currentPage, totalPages, len(photos)))
	result.result = photos
	database.storeApiResponse(db, result)
	return result

def getExifDataOf(db, photoid):
	'''	Returns the EXIF data of the given photo '''
	logMessage('flickr', 'Getting EXIF information for photo %s' % (photoid))
	result = callFlickrAPI(db, 'flickr.photos.getExif', {'photo_id': photoid}, photoid)
	if not result.cached: database.storeApiResponse(db, result)
	return result

def getCommentsOf(db, photoid):
	'''	Returns the comments of the given photo '''
	logMessage('flickr', 'Getting Comments information for photo %s' % (photoid))
	result = callFlickrAPI(db, 'flickr.photos.comments.getList', {'photo_id': photoid}, photoid)
	if not result.cached: database.storeApiResponse(db, result)
	return result

def getLicensesInfo(db):
	''' Returns the Licenses available on flickr '''
	logMessage('flickr', 'Getting license information')
	result = FlickrResponse('flickr.photos.licenses.getInfo', {}, '', None)
	if result.loadFromCache(db):
		return result

	result = callFlickrAPI(db, 'flickr.photos.licenses.getInfo')
	result.result = result.result['licenses']['license']
	if not result.cached: database.storeApiResponse(db, result)
	return result