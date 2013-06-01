function ImageListCtrl($scope, $http) {
	$scope.search_string = "";
	$scope.matches = 0;
	$scope.search_time = 0;
	$scope.images = [];

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
	var search_lock = false;
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
		if(last_search_term == $scope.search_string) return;
		if(search_lock) return;
		search_lock = true;
		last_search_term = $scope.search_string;
		console.log("Lock Acquired for " + last_search_term);

		var params;
		if ($scope.advanced_search) {
			params = {
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
			params = {q: last_search_term };
		}

		$http({
			url: 'api',
			method: 'GET',
			params: params
		}).success(function(data) {
			$scope.images = data;
			$scope.selection = null;


			// Defere lock release
			setTimeout(function() {
				// Release the lock!
				console.log("Lock released");
				search_lock = false;

				// Has the search string changed in the meantime?
				if(last_search_term != $scope.search_string)
					$scope.search();
			}, 50);
		});
	};

	// Handle image selection
	$scope.select = function(image) {
		$scope.selection = image;
	};

	// Handle advanced options
	$scope.toggleOptions = function() {
		$scope.advanced_search = !$scope.advanced_search;
		last_search_term = "";
		$scope.deferredSearch();
	}

	// Detect advanced options changed
	$scope.$watch('advanced_options', function () { last_search_term = ""; $scope.deferredSearch(); }, true);
}