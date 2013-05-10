import psycopg2, getpass, time, json
from utils import logMessage

def convertFromPosix(p):
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(p)))

def getDatabaseConnection():
	dbhost = input('PSQL host [localhost]: ')
	if dbhost == '': dbhost = 'localhost'
	dbuser = input('PSQL user [postgres]: ')
	if dbuser == '': dbuser = 'postgres'
	dbpass = getpass.getpass('PSQL pass [postgres]: ')
	if dbpass == '': dbpass = 'postgres'
	dbname = input('PSQL name [flickr]: ')
	if dbname == '': dbname = 'flickr'

	return psycopg2.connect(host=dbhost, database=dbname, user=dbuser, password=dbpass)

def rawSqlQuery(db, sql, args):
	cur = db.cursor()
	cur.execute(sql, args)
	db.commit()
	cur.close()

def storeApiResponse(db, response):
	cur = db.cursor()
	logMessage('psql', 'Inserting response of \'%s\' api call' % (response.method))
	cur.execute('INSERT INTO flickr_api (hash, api, params, main_arg, response) VALUES(%s, %s, %s, %s, %s)',
		(response.digest(), response.method, json.dumps(response.params), response.main_arg, json.dumps(response.result)))
	db.commit()
	cur.close()

def resultsExistFor(db, method, main_arg=None):
	cur = db.cursor()

	message = 'Checking if results exist for \'%s\'' % (method)

	if main_arg == None:
		cur.execute('SELECT count(*) FROM flickr_api WHERE api = %s', [method])
	else:
		message += ' (%s)' % (main_arg)
		cur.execute('SELECT count(*) FROM flickr_api WHERE api = %s AND main_arg = %s', (method, main_arg))

	t = cur.fetchone()
	if t[0] == 0:
		message += ": NO"
	else:
		message += ": YES (" + str(t[0]) + " tuples)"

	logMessage('psql', message)

	db.commit()
	cur.close()
	return t[0] != 0

def getCachedResultsFor(db, digest):
	cur = db.cursor()
	cur.execute('SELECT response FROM flickr_api WHERE hash = %s', [digest])
	t = cur.fetchone()
	db.commit()
	cur.close()

	if t != None:
		logMessage('psql', 'Fetched cached response')
		return t[0]
	else:
		return None

def etlInsertPhoto(conn, photos): 
	cur = conn.cursor()
	for photo in photos:
		cur.execute('SELECT COUNT(*) FROM flat_photos where id = %s', [photo.id])
		r = cur.fetchone()
		if r[0] == 0:
			q = ( 'INSERT INTO flat_photos(id, owner, url, width, height, views, title,'
				 'latitude, longitude, license, machine_tags, dateupload, description, last_update,'
				 'ownername, pathalias, datetaken, tags, comments, camera, lens, exposure, aperture, focal_length, iso_speed, thumbnail_url )'
				 'VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s, %s, %s ,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)'
				)

			cur.execute(q, (photo.id, photo.owner, photo.url, photo.width, photo.height, photo.views, photo.title
				,photo.latitude, photo.longitude, photo.license, photo.machine_tags, photo.dateupload,photo.description, photo.last_update
				,photo.ownername, photo.pathalias, photo.datetaken, photo.tags, photo.comments, photo.camera, photo.lens, photo.exposure
				,photo.aperture, photo.focal_length, photo.iso_speed, photo.thumbnail))
	conn.commit()
	cur.close()


