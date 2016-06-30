# Facebook scraper

A tool for retrieving posts, comments, likes, reactions and active users' information from public Facebook pages, groups, events, etc. The
output is a SQLite database with four tables for posts, comments, likes and people.


## Installation

### Linux/OS X
The scraper should work both with Python 2 and 3.

Install following Python libraries:
```
pip install facebook-sdk
pip install simplejson
```
Download FBscraper repository and unzip it on your computer.

### Windows
The scraper should work both with Python 2 and 3. If you don't have Python install [Anaconda](https://www.continuum.io/downloads#_windows). Then edit your environment variables like [here](http://stackoverflow.com/questions/3701646/how-to-add-to-the-pythonpath-in-windows-7).

Open command prompt window and install the following Python libraries:
```
pip install facebook-sdk
conda install simplejson
```
Download FBscraper repository and unzip it on your computer.

## Running

To run the scraper you should provide three things to the script on the command line:

1. Your own Facebook access token

    To get a token visit: https://developers.facebook.com/tools/explorer/. It may expire after a while, renew it then.

2. The path to the SQlite database in which you want to store the data

    The scraper can also create a database or store data in an existing one, both by giving the proper path and the name. (.sqlite extension is required).
    
3. The Facebook ID of the page you want to get the data from

    * In case of Facebook events, groups and communities the ID can be found easily, usually, it is the last group of numbers at the end of the URL:
    https://www.facebook.com/events/XXXXXXXXXXXXX or https://www.facebook.com/groups/XXXXXXXXXXXXX
   
    * You can find the ID in the page source too. Press ctrl+u then use the find tool of your browser (usually ctrl+f) and search for the type of the page, something like content="fb://page/XXXXXXXXXXX" or content="fb://profile/XXXXXXXXXXX".
    
    * Or just use one from the many online ID founder like [this](http://www.findmyfbid.com/).

Note that the scraper does not process personal pages, you can only scrape public information from public pages. If you use the scraper, please read more on Facebook's data policy and act according to it. Also, please follow the basic data protection guidelines! https://www.facebook.com/full_data_use_policy, https://ico.org.uk/for-organisations/guide-to-data-protection/


### Windows

Change directory to FBscraper folder in command line:
```
cd your\path\to\FBscraper
```

### Linux/OS X
Change directory to FBscraper directory:
```
cd your/path/to/FBscraper
```
### Windows/Linux/OS X
After changing directory you can run scrapeFB.py. There are two ways:

1. Run scrapeFB.py with dashes:

    -a or `--`access_token: to give Facebook access token
    
    -d or `--`db_path: to give the path of the SQLite database
    
    -i or `--`id_list: to give the Facebook IDs
    
    ```
    python scrapeFB.py -a l0ngL0nGtOkEn -d ..\data\fbpagename.sqlite -i 123456789101112
    ```

2. Run scrapeFB.py in interactive mode:

    Mind the single quotes and the square brackets.
    ```
    python scrapeFB.py
    Please type your own Facebook access token: 'l0ngL0nGtOkEn'
    Please type the path of the SQLite database in which you want to store the data: '..\data\fbpagename.sqlite'
    Please type the ID's of the Facebook pages you want to scrape: ['123456789101112']
    ```

## Database

After processing you can find the data in the given SQLite database file. The database contains tables 'Posts', 'Comments', 'Post_likes' and 'People' with the scraped data. To view the database use a SQL browser e.g. [DB Browser for SQLite](https://github.com/sqlitebrowser/sqlitebrowser).

The database scheme looks following:

![ ](https://raw.github.com/precognox-admin/FBscraper/img/scheme.png "Database scheme")

Note that published_date and last_comment_date are in GMT.


## Release notes

### Copyleft
The scraper is free by any means and comes with absolutely no warranty. 

### Data protection
Be kind when you are scraping Facebook data! Follow Facebook’s rules, and also think about research ethics twice before you publish your results!

### You can cite us
You make us happy if you refer to this github repo when you use it for any purposes and publish your results.

### Contact
You can reach us at keresovilag(at)precognox.com 

### Team
Kitti Balogh ([@kttblgh](https://twitter.com/kttblgh))
Nora Fulop
Zoltan Varju ([@zoltanvarju](https://twitter.com/zoltanvarju))