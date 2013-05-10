<!doctype html>
<html ng-app>
	<head>
		<meta charset="utf-8">
		<title>Angular tests</title>

		<!-- Make it sexy -->
		<link rel="stylesheet" href="css/style.css">

		<!-- Load Angular and let magic happen -->
		<script src="components/angular/angular.js"></script>
		<script src="javascript/script.js"></script>
	</head>
	<body>
		<div ng-controller="ImageListCtrl">
			<header class="search-bar">
				Search: <input type="text" ng-model="search_string" ng-change="deferredSearch()">
				<button class="search-button" ng-click="search()"></button>
			</header>

			<section class="context-window">
				<p class="search-statistics">Found {{images.length}} results in {{search_time | number:2}}s</p>
				<h1>{{selection.title}}</h1>
				<img ng-hide="!selection" src="{{selection.url}}" alt="">
				<p>{{selection.description}}</p>
			</section>

			<section class="search-results">
				<ul class="results">
					<li ng-repeat="image in images" ng-click="select(image)">
						<h2 class="title-panel">{{image.title}}</h2>
						<div class="thumbnail-panel">
							<img src="{{image.thumbnail_url}}" alt="{{image.image_title}}">
						</div>
						<div class="description-panel">
							<ul class="tech-specs">
								<li class="resolution" ng-hide="!image.resolution">{{image.width}}x{{image.height}}</li>
								<li class="aperture" ng-hide="!image.aperture">{{image.aperture}}</li>
								<li class="shutter-speed" ng-hide="!image.exposure">{{image.exposure}}</li>
								<li class="iso"ng-hide="!image.iso_speed">{{image.iso_speed}}</li>
							</ul>
							<div class="image-description">
								<p ng-bind-html-unsafe="image.description"></p>
							</div>
						</div>
					</li>
				</ul>
			</section>
		</div>

	</body>
</html>