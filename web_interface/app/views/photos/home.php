<!doctype html>
<html ng-app="irProject">
	<head>
		<meta charset="utf-8">
		<title>Image Search Engine</title>

		<!-- Make it sexy -->
		<link rel="stylesheet" href="css/style.css">

		<!-- Load Angular and let magic happen -->
		<script src="components/jquery/jquery.js"></script>
		<script src="components/angular/angular.js"></script>
		<script src="components/ngInfiniteScroll/ng-infinite-scroll.js"></script>
		<script src="javascript/script.js"></script>
	</head>
	<body>
		<div ng-controller="ImageListCtrl">
			<header class="search-bar">
				<h1>Search:</h1> <input type="text" ng-model="search_string" ng-change="deferredSearch()" class="search-field">
				<button class="search-button" ng-click="search()"></button>
				<button class="toggle-options-button" ng-click="toggleOptions()"></button>

				<section class="advanced-search" ng-hide="!advanced_search">
					<p>
						<label for="main-search-field">main search field:</label>
						<select name="main-search-field" ng-model="advanced_options.main_field">
							<option value="title">Title</option>
							<option value="description">Description</option>
							<option value="tags">Tags</option>
							<option value="comments">Comments</option>
						</select>
					</p>
					<p>
						<label>ISO range:</label>
						<input type="text" ng-model="advanced_options.min_iso"> to <input type="text" ng-model="advanced_options.max_iso">
					</p>
					<p>
						<label >Exposure range:</label>
						<input type="text" ng-model="advanced_options.min_exposure"> to <input type="text" ng-model="advanced_options.max_exposure"> s
					</p>
					<p>
						<label>Aperture range (F value):</label>
						<input type="text" ng-model="advanced_options.min_aperture"> to <input type="text" ng-model="advanced_options.max_aperture">
					</p>
					<p>
						<label>Focal Length range:</label>
						<input type="text" ng-model="advanced_options.min_focallength"> to <input type="text" ng-model="advanced_options.max_focallength"> mm
					</p>
				</section>
			</header>

			<section class="context-window">
				<p class="search-statistics">Found {{images.length}} results in {{search_time | number:2}}s</p>
				<h1>{{selection.title}}</h1>
				<img ng-hide="!selection" ng-src="{{selection.url}}" alt="">
				<p>{{selection.description}}</p>
			</section>

			<section class="search-results"  infinite-scroll="loadNextPage()" infinite-scroll-distance="1">
				<ul class="results" >
					<li ng-repeat="image in images" ng-click="select(image)">
						<h2 class="title-panel">{{image.title}}</h2>
						<div class="thumbnail-panel">
							<img ng-src="{{image.thumbnail_url}}" alt="{{image.image_title}}">
						</div>
						<div class="description-panel">
							<ul class="tech-specs">
								<li class="resolution" ng-hide="!image.resolution">{{image.width}}x{{image.height}}</li>
								<li class="aperture" ng-hide="!image.aperture">{{image.aperture}}</li>
								<li class="shutter-speed" ng-hide="!image.exposure">{{image.exposure}}</li>
								<li class="iso"ng-hide="!image.iso_speed">{{image.iso_speed}}</li>
							</ul>
							<div class="image-description">
								<p>
									{{image.description | truncate:150:"..."}}
								</p>
							</div>
							<div class="more-like-this-panel">
								<button ng-click="moreLikeThis(image)">More Like This</button>
							</div>								
						</div>
					</li>
				</ul>
			</section>
		</div>

	</body>
</html>
