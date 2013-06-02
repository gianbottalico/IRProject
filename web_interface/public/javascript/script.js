angular.module('irProject', ['filters', 'infinite-scroll']);


angular.module('filters', []).
    filter('truncate', function () {
        return function (text, length, end) {
            if (isNaN(length))
                length = 10;

            if (end === undefined)
                end = "...";

            if (text.length <= length || text.length - end.length <= length) {
                return text;
            }
            else {
                return String(text).substring(0, length-end.length) + end;
            }

        };
    });

function ImageListCtrl($scope, $http) {
	$scope.search_string = "";
	$scope.matches = 0;
	$scope.search_time = 0;
	$scope.search_params = {};
	$scope.search_url = '';

	$scope.current_page = -1; 
	$scope.images = [];
	var max_images_per_page = 30;
	$scope.last_search_results = -1;

	$scope.advanced_search = false;
	$scope.advanced_options = {
		main_field:      'title',
		min_iso:         50,
		max_iso:         256000,
		min_exposure:    '1/8000',
		max_exposure:    60,
		min_aperture:    0.5,
		max_aperture:    32,
		min_focallength: 5,
		max_focallength: 4000
	}

	// Deferred search handling
	var last_search_term = "";
	var deferredSearchTimeout;
	$scope.deferredSearch = function() {
		if(deferredSearchTimeout) {	
			clearTimeout(deferredSearchTimeout);
			deferredSearchTimeout = null;
		}

		deferredSearchTimeout = setTimeout(function() {
			$scope.search();
		}, 300);
	}

	$scope.search = function() {
		if(last_search_term == $scope.search_string) { 
			return;
		}
		if($scope.search_lock) {
			return;
		}

		$scope.search_lock = true;
		last_search_term = $scope.search_string;
		console.log("Lock Acquired for " + last_search_term);

		if ($scope.advanced_search) {
			$scope.search_params = {
				q: last_search_term,
				main_field:      $scope.advanced_options.main_field,
				min_iso:         $scope.advanced_options.min_iso,
				max_iso:         $scope.advanced_options.max_iso,
				min_exposure:    $scope.advanced_options.min_exposure,
				max_exposure:    $scope.advanced_options.max_exposure,
				min_aperture:    $scope.advanced_options.min_aperture,
				max_aperture:    $scope.advanced_options.max_aperture,
				min_focallength: $scope.advanced_options.min_focallength,
				max_focallength: $scope.advanced_options.max_focallength
			};
		} else {
			$scope.search_params = {q: last_search_term };
		}

		$scope.search_url = 'api';
		$scope.current_page = 0;
		$scope.search_lock = false;
		$scope.last_search_results = -1;
		$scope.loadNextPage();
	};

	// Handle image selection
	$scope.select = function(image) {
		$scope.selection = image;
	};

	// Handle More Like This Search
	$scope.moreLikeThis = function(image) {

		$scope.search_params = {
			q: image.id
		}
		$scope.search_url = 'morelikethis';
		$scope.current_page = 0;
		$scope.last_search_results = -1;
		
		$scope.loadNextPage();
	}

	// Get Next Result Page
	$scope.loadNextPage = function() {
		
		if ( $scope.current_page == -1 ) {
			return;
		}
		if ($scope.search_lock) {
			return;
		}
		//last page is reached 
		if ($scope.last_search_results != -1 && $scope.last_search_results < max_images_per_page)
		{
			return;
		} 
		//Reset images data if a new search occours
		if ($scope.current_page == 0) {
			$scope.images = [];
		}

		$scope.search_lock = true;

		$scope.search_params['current_page'] = $scope.current_page += 1;

		$http({
			url: $scope.search_url,
			method: 'GET',
			params: $scope.search_params
		}).success(function(data) {
			$scope.last_search_results = data.length;
			$scope.images.push.apply($scope.images,data);
			//unbind context windows only on first page
			if ($scope.current_page == 1) {
				$scope.selection = null;
			}
			// Defere lock release
			setTimeout(function() {
				// Release the lock!
				console.log("Lock released");
				$scope.search_lock = false;

				// Has the search string changed in the meantime?
				if(last_search_term != $scope.search_string)
					$scope.search();
			}, 50);
		}).error(function(){
			// Release the lock!
			console.log("Lock released");
			$scope.search_lock = false;
		});
	}
	// Handle advanced options
	$scope.toggleOptions = function() {
		$scope.advanced_search = !$scope.advanced_search;
		last_search_term = "";
		$scope.deferredSearch();
	}

	// Detect advanced options changed
	$scope.$watch('advanced_options', function () { last_search_term = ""; $scope.deferredSearch(); }, true);
}