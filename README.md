IRProject
=========

A Free and Open Source images retrieval system for the Recommender Systems and Information Retrieval course of Free University of Bozen.

The projects includes a utility, to locally backup and browse your flickr photos. In order for the flickrbackup utility to work, you need to create a file named secret.py, containing the api key:

    api_key = 'my-secret-flickr-api-key'

Furthermore you will need to have an active SOLR and Postgresql servers running, and access to them.

You will need to provide as an input to the utility, a file containing your flickr accounts. Please keep in mind that the first 15 characters, will be checked for account numbers e.g:

    1234567890@12   # My first accout
    1234567891@12   # My second accout

Finally, the utility can be called as following:

    python3 main.py accounts_file.txt

Authors
-----------------
* Gianluca Bottalico
* Denis Declara

Course Site
--------------
http://www.gnuband.org/recommender_systems_and_information_retrieval/index.php?title=Main_Page
