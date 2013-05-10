function ImageListCtrl($scope, $http) {
	$scope.search_string = "";
	$scope.matches = 0;
	$scope.search_time = 0;
	$scope.images = [];

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

		$http({
			url: 'api',
			method: 'GET',
			params: {q: last_search_term}
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

	$scope.select = function(image) {
		$scope.selection = image;
	};
}