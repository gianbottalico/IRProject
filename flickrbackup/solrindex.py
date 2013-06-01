import pysolr
import json
from time import strptime

_solr_instance = None

def initSolr():
	global _solr_instance
	solrurl = input('SOLR url [http://localhost:8983/photos]: ')
	if solrurl == '': solrurl = 'http://localhost:8983/photos'
	_solr_instance = pysolr.Solr('http://localhost:8983/photos')

def fixdate(d):
	if d is None: return ''
	datestr = str(d)
	if len(datestr) == 0: return ''
	return datestr[0:10] + "T" + datestr[11:19] +  "Z"

def addToSolrIndex(pictures):
	docs = []


	for picture in pictures:
		doc = {
			'id':           picture.id,
			'ownername':    picture.ownername,
			'title':        picture.title,
			'description':  picture.description,
			'comments':     picture.comments,
			'tags':         picture.tags,
			'width':        picture.width,
			'height':       picture.height,
			'license':      picture.license,
			'latitude':     picture.latitude,
			'longitude':    picture.longitude,
			'datetaken':    fixdate(picture.datetaken),
			'camera':       picture.camera,
			'lens':         picture.lens,
			'exposure':     picture.c_exposure,
			'aperture':     picture.c_aperture,
			'focal_length': picture.c_focal_length,
			'iso':          picture.c_iso_speed,
			'dateuploaded': fixdate(picture.dateupload),
			'last_update':  fixdate(picture.last_update)
		}

		docs.append(doc)
	_solr_instance.add(docs)

def deleteSolrIndex():
	_solr_instance.delete(q='*:*')
