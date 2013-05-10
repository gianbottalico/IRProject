describe('Images controllers', function() {

	describe('ImageListCtrl', function() {

		it('should create "images" model with 2 photos', function() {
			var scope = {}, ctrl = new ImageListCtrl(scope);
			expect(scope.images.length).toBe(0);
		});
	});
});