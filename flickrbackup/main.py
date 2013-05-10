from flickrapi import *
from database import *
from utils import bgc
from etl import IrEtl
from solrindex import *
import time, argparse, sys


def createTables(db):
	rawSqlQuery(db, '''
		CREATE TABLE IF NOT EXISTS flickr_api (
			hash         char(40)     NOT NULL PRIMARY KEY,
			api          varchar(256) NOT NULL,
			params       json         NOT NULL,
			main_arg     varchar(256) NOT NULL,
			response     json         NOT NULL,
			request_time timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP
		);''', [])
	rawSqlQuery(db, '''
		CREATE TABLE IF NOT EXISTS flat_photos (
			id            bigint       NOT NULL PRIMARY KEY,
			owner         varchar(255) NOT NULL,
			url           varchar(255) NOT NULL,
			width         int          NOT NULL,
			height        int          NOT NULL,
			license       varchar(255) NOT NULL,
			latitude      varchar(255) NOT NULL,
			longitude     varchar(255) NOT NULL,
			machine_tags  varchar(255) NOT NULL,
			views         int          NOT NULL,
			description   text         NOT NULL,
			title         varchar(600) NOT NULL,
			datetaken     timestamp(6),
			ownername     varchar(300) NOT NULL,
			pathalias     varchar(255) NOT NULL,
			tags          text         NOT NULL,
			comments      text         NOT NULL,
			camera        varchar(255) NOT NULL,
			lens          varchar(255) NOT NULL,
			exposure      varchar(255) NOT NULL,
			aperture      varchar(255) NOT NULL,
			focal_length  varchar(255) NOT NULL,
			iso_speed     varchar(255) NOT NULL,
			dateupload    timestamp(6),
			last_update   timestamp(6),
			thumbnail_url varchar(255) NOT NULL
		);''', [])




if __name__ == '__main__':
	argparser = argparse.ArgumentParser(description='Populate database and SOLR index from Flickr.')
	argparser.add_argument('accounts_file', metavar='ACCOUNTS_FILE', type=str, help='File from which to read the account list. Accounts should be divided by lines, and should occupy the first 15 columns, or pad with spaces')
	argparser.add_argument('--truncate-solr-index', help='Deletes all data in the solr index and EXITS.', action='store_true')
	argparser.add_argument('--truncate-etl-data', help='Deletes all the transformed data in the database and EXITS.', action='store_true')
	argparser.add_argument('--update-photo-lists', help='Redownloads the photo list of all users and fetches eventual new photos.', action='store_true')
	argparser.add_argument('--no-etl',   help='Stores the flickr api requests in the database cache, and does not normalize the data. Also the SOLR index will not be written using this flag.', action='store_true')
	argparser.add_argument('--no-index', help='Does not write to the SOLR index.', action='store_true')
	argparser.add_argument('--no-color', help='Disables color output.', action='store_true')
	argparser.add_argument('--step', type=int, help='Interval, at which data is written to the ETL table or SOLR index', default=1000)
	argparser.add_argument('--shard', type=int, help='Used to run multiple instances concurrently, first argument is the number of shards, second is the shard index [1-N].', nargs=2, default=[1,0])

	args = argparser.parse_args();

	init_solr = not args.no_index or args.truncate_solr_index
	init_db   = not args.truncate_solr_index

	db = None
	etl = None
	if init_db:
		db = getDatabaseConnection()
		createTables(db)
		etl = IrEtl(db)
	if init_solr:
		initSolr()

	# Truncate SOLR index
	if args.truncate_solr_index:
		deleteSolrIndex()
		print("SOLR index deleted")
		sys.exit(0)
	
	# Disable color
	if args.no_color:
		bgc.disable()

	# Truncate ETL data
	if args.truncate_etl_data:
		rawSqlQuery(db, 'DELETE FROM flat_photos', [])
		print("ETL data deleted")
		sys.exit(0)

	getLicensesInfo(db)

	# Open accounts
	accountsFile = open(args.accounts_file, 'r')
	accounts = [x[0:15].strip() for x in accountsFile]
	
	for who in accounts:
		print("Processing photos of %s" % who)
		# who = input("Whose photos shall we grab: ")

		# Let's get the photos
		photos = getPhotosOf(db, who)
		spics = []

		i = 0
		parsedImages = 0
		for photo in photos.result:
			photoID = photo['id']

			i += 1

			if i % args.shard[0] != (args.shard[1] % args.shard[0]): continue

			parsedImages += 1
			print(("Processing photo %i out of %i by " + bgc.warning + "%s" + bgc.endc + ": " + bgc.header + "%s" + bgc.endc) % (i, len(photos.result), photo['ownername'], photo['title']))

			exif = getExifDataOf(db, photoID).result
			comments = getCommentsOf(db, photoID).result

			spic = etl.etl(photo, exif, comments)
			spics.append(spic)
			if parsedImages % args.step == 0:
				if not args.no_etl:
					print(" > Committing ETL data")
					etl.commit()
				if not args.no_index:
					print(" > Adding to SOLR index")
					addToSolrIndex(spics)
					spics = []


		if not args.no_etl:	
			print(" > Committing ETL data")
			etl.commit()
		if not args.no_index and len(spics) != 0:
			print(" > Adding to SOLR index")
			addToSolrIndex(spics)
			spics = []