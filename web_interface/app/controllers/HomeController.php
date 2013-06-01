<?php

class HomeController extends BaseController {

	/*
	|--------------------------------------------------------------------------
	| Default Home Controller
	|--------------------------------------------------------------------------
	|
	| You may wish to use controllers instead of, or in addition to, Closure
	| based routes. That's great! Here is an example controller method to
	| get you started. To route to this controller, just add the route:
	|
	|	Route::get('/', 'HomeController@showWelcome');
	|
	*/

	public function __construct() {
		$this->solr_endpoint = array(
			'endpoint' => array(
				'localhost' => array(
					'host' => 'localhost',
					'port' => 8983,
					'path' => '/photos',
				)
			)
		);
	}

	private static function parse_number($input) {
		if (empty($input)) return null;
		if (strstr($input, "/") !== false) {
			$splitters = explode("/", $input);
			if (count($splitters) != 2) return null;
			$a = self::parse_number($splitters[0]);
			$b = self::parse_number($splitters[1]);
			if ($b == 0) return null;
			return $a / $b;
		} elseif (is_numeric($input)) {
			return (float)$input;
		} else {
			return null;
		}
	}

	public function index()
	{
		return View::make('photos.home');
	}

	public function api()
	{
		$q = Input::get('q');
		$simple_query = !Input::has('main_field');

		$client = new Solarium\Client($this->solr_endpoint);

		// get an update query instance
		$query = $client->createselect();
		$dismax = $query->getEDisMax();

		// Advanced query
		$query_weights = array(
			'title'       => 'title^5.0 description^0.2 tags^0.2 comments^0.1',
			'description' => 'title^0.2 description^5.0 tags^0.2 comments^0.1',
			'tags'        => 'title^0.2 description^0.2 tags^5.0 comments^0.1',
			'comments'    => 'title^0.2 description^0.2 tags^0.1 comments^5.0',
			'default'     => 'title^1.5 description^1.0 tags^5.0 comments^0.1',
		);

		if($simple_query) {
			// Simple query!
			$dismax->setQueryFields($query_weights['default']);
		} else {
			$main_field = Input::get('main_field');
			if (array_key_exists($main_field, $query_weights))
			{
				$dismax->setQueryFields($query_weights[$main_field]);
			} else {
				$dismax->setQueryFields($query_weights['default']);
			}

			$helper = $query->getHelper();

			// Filter by ISO:
			$iso_min = self::parse_number(Input::get('min_iso'));
			$iso_max = self::parse_number(Input::get('max_iso'));
			if (!is_null($iso_min) && !is_null($iso_max)) {
				$query->createFilterQuery('iso_filter')->setQuery($helper->rangeQuery('iso', $iso_min, $iso_max));
			}

			// Filter by Exposure:
			$exposure_min = self::parse_number(Input::get('min_exposure'));
			$exposure_max = self::parse_number(Input::get('max_exposure'));
			if (!is_null($exposure_min) && !is_null($exposure_max)) {
				$query->createFilterQuery('exposure_filter')->setQuery($helper->rangeQuery('exposure', $exposure_min, $exposure_max));
			}

			// Filter by Aperture:
			$aperture_min = self::parse_number(Input::get('min_aperture'));
			$aperture_max = self::parse_number(Input::get('max_aperture'));
			if (!is_null($aperture_min) && !is_null($aperture_max)) {
				$query->createFilterQuery('aperture_filter')->setQuery($helper->rangeQuery('aperture', $aperture_min, $aperture_max));
			}

			// Filter by Focal Length:
			$focallength_min = self::parse_number(Input::get('min_focallength'));
			$focallength_max = self::parse_number(Input::get('max_focallength'));
			if (!is_null($focallength_min) && !is_null($focallength_max)) {
				$query->createFilterQuery('focallength_filter')->setQuery($helper->rangeQuery('focal_length', $focallength_min, $focallength_max));
			}
		}

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
	}
}