<?php

/*
|--------------------------------------------------------------------------
| Application Routes
|--------------------------------------------------------------------------
|
| Here is where you can register all of the routes for an application.
| It's a breeze. Simply tell Laravel the URIs it should respond to
| and give it the Closure to execute when that URI is requested.
|
*/

Route::get('/deleteindex', function() {
	$config = array(
		'endpoint' => array(
			'localhost' => array(
				'host' => 'localhost',
				'port' => 8983,
				'path' => '/photos',
			)
		)
	);
	
	$client = new Solarium\Client($config);

	// get an update query instance
	$update = $client->createUpdate();

	// add the delete query and a commit command to the update query
	$update->addDeleteQuery('*:*');
	$update->addCommit();

	// this executes the query and returns the result
	$result = $client->update($update);

	return "done!";
});

Route::get('/api', function() {
	$q = Input::get('q');

	$config = array(
		'endpoint' => array(
			'localhost' => array(
				'host' => 'localhost',
				'port' => 8983,
				'path' => '/photos',
			)
		)
	);
	
	$client = new Solarium\Client($config);

	// get an update query instance
	$query = $client->createselect();

	$dismax = $query->getEDisMax();
	$dismax->setQueryFields('title^1.5 description^1 comments^0.1');

	$query->setQuery($q);
	$query->setRows(50);
	$query->setFields(array('id'));
	$resultset = $client->select($query);

	$ids = array();
	foreach($resultset as $document) {
		$photo = Photo::find($document->id);
		$ids[]= $photo->toArray();
	}

	return json_encode($ids);
});

Route::get('/index', function() {
	$photos = Photo::take(5000)->skip(30000)->get();

	$config = array(
		'endpoint' => array(
			'localhost' => array(
				'host' => 'localhost',
				'port' => 8983,
				'path' => '/photos',
			)
		)
	);
	
	$client = new Solarium\Client($config);
	$update = $client->createUpdate();

	foreach ($photos as $photo) {
		$doc = $update->createDocument();

		$doc->id           = $photo->id;
		$doc->ownername    = $photo->ownername;
		$doc->title        = $photo->title;
		$doc->description  = $photo->description;
		$doc->comments     = $photo->comments;
		$doc->tags         = $photo->tags;
		$doc->width        = $photo->width;
		$doc->height       = $photo->height;
		$doc->license      = $photo->license;
		$doc->latitude     = $photo->latitude;
		$doc->longitude    = $photo->longitude;
		$doc->datetaken    = gmdate('Y-m-d\TH:i:s\Z', strtotime($photo->datetaken));
		$doc->camera       = $photo->camera;
		$doc->lens         = $photo->lens;
		$doc->exposure     = $photo->exposure;
		$doc->aperture     = $photo->aperture;
		$doc->focal_length = $photo->focal_length;
		$doc->iso          = $photo->iso;
		$doc->dateuploaded = gmdate('Y-m-d\TH:i:s\Z', strtotime($photo->dateupload));
		$doc->last_update  = gmdate('Y-m-d\TH:i:s\Z', strtotime($photo->last_update));

		$update->addDocument($doc);
	}

	$update->addCommit();
	$result = $client->update($update);

	return "done! cosa?" . $result->getStatus() . " (" . $result->getQueryTime() . ")";
});

Route::get('/', function()
{
	return View::make('photos.home');
});