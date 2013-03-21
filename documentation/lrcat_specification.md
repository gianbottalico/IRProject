The adobe .lrcat v4 file format
============================

The file is essentially a sqlite database, containing all the information about the images. In the following sections we will discuss some of the tables and the data they contain.

The information presented here is the result of reverse engineering and intuation. Therefore this documentation might be incorrect, and clearly isn't meant to be complete.

The *adobe_images* table
----------------------

This tables contains all the basic information about images, the most important fields are the following:

* **id_local**: Id of the image
* **id_global**: GUID of the image
* **aspectRatioCache**: Stores the aspect ratio of the image (width / height) after being cropped
* **captureTime**: Time at which the photo was shot
* **colorLabels**: Color label of the image. Stored as the name of the color, e.g. "Green"
* **fileFormat**: Format of the file, typically one of the following values: *JPG*, *RAW*, *TIFF*, *VIDEO*, ...
* **fileWidth**: Width in pixels of the image.
* **fileHeight**: Height in pixels of the image. Note, this information is not affected by the image orientation.
* **orientation**: A two letter combination, can be either *AB* *BC* *CD* or *DA*. Where *AB* is the neutral orientation, and every successive pair, indicates a 90° rotation w.r.t. the previous. (Needs further testing though)

**NOTE**: This table does not actually contain any reference to the actual image file, but rather is just an index of the images contained in the catalog.

The *agLibraryRootFolder* table
-------------------------------

This table contains the root directory, in which the photos are stored on the system.

* **id_local**: Id of the root folder
* **id_global**: GUID of the root folder
* **absolutePath**: Absolute path to the photos
* **name**: Name of the path
* **relativePathFromCatalog**: Relative path to the folder from where the .lrcat file is located. Note that this field might be null if e.g. the folder is on another drive w.r.t. the cathalog file.


Reconstructing import history
-----------------------------

Lightroom stores information about the date and time a photo was added to the catalog. In the table *agLibraryImportImage* an *iamge* is linked to a specific *import*. The latter field is a foreign key to the *agLibraryImport* table, which contains the date the import has been carried out.