<?php

class HomeController extends BaseController {

	private $imagesPerPage = 30;

	public function __construct() {
		$this->solr_endpoint = array(
			'endpoint' => array(
				'localhost' => array(
					'host' => 'localhost',
					'port' => 8983,
					'path' => '/solr',
				)
			)
		);
	}

	public function index()
	{
		return View::make('photos.home');
	}

	public function api()
	{
		$q = Input::get('q');
		$current_page = Input::get('current_page');
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
			$iso_min = Helper::parseNumber(Input::get('min_iso'));
			$iso_max = Helper::parseNumber(Input::get('max_iso'));
			if (!is_null($iso_min) && !is_null($iso_max)) {
				$query->createFilterQuery('iso_filter')->setQuery($helper->rangeQuery('iso', $iso_min, $iso_max));
			}

			// Filter by Exposure:
			$exposure_min = Helper::parseNumber(Input::get('min_exposure'));
			$exposure_max = Helper::parseNumber(Input::get('max_exposure'));
			if (!is_null($exposure_min) && !is_null($exposure_max)) {
				$query->createFilterQuery('exposure_filter')->setQuery($helper->rangeQuery('exposure', $exposure_min, $exposure_max));
			}

			// Filter by Aperture:
			$aperture_min = Helper::parseNumber(Input::get('min_aperture'));
			$aperture_max = Helper::parseNumber(Input::get('max_aperture'));
			if (!is_null($aperture_min) && !is_null($aperture_max)) {
				$query->createFilterQuery('aperture_filter')->setQuery($helper->rangeQuery('aperture', $aperture_min, $aperture_max));
			}

			// Filter by Focal Length:
			$focallength_min = self::parseNumber(Input::get('min_focallength'));
			$focallength_max = self::parseNumber(Input::get('max_focallength'));
			if (!is_null($focallength_min) && !is_null($focallength_max)) {
				$query->createFilterQuery('focallength_filter')->setQuery($helper->rangeQuery('focal_length', $focallength_min, $focallength_max));
			}
		}

		$query->setQuery($q);
		//Pagination
		$query->setStart(($current_page -1 ) * $this->imagesPerPage)->setRows($this->imagesPerPage);
		$query->setFields(array('id'));
		$resultset = $client->select($query);

		$ids = array();
		foreach($resultset as $document) {
			$photo = Photo::find($document->id);
			$ids[]= $photo->toArray();
		}

		return json_encode($ids);
	}

	public function more() {
		$id= Input::get('q');
		$current_page = Input::get('current_page');
		
		$client = new Solarium\Client($this->solr_endpoint);

		$mltQuery = $client->createMoreLikeThis();
		//Prepare Query
		$mltQuery->setQuery("id:$id");
		$mltQuery->setMltFields('ownername, title, description, comments');
		$mltQuery->setMinimumDocumentFrequency(1);
		$mltQuery->setMinimumTermFrequency(1);

		//Pagination
		$mltQuery->setStart(($current_page -1 ) * $this->imagesPerPage)->setRows($this->imagesPerPage);
		
		$mltQuery->setFields(array('id'));
		$result = $client->select($mltQuery);
		$ids = array();
		foreach($result as $document) {
			$photo = Photo::find($document->id);
			$ids[]= $photo->toArray();
		}

		return json_encode($ids);
	}
}
