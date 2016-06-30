### Scrape sample databases

## before running
# change directory to FBscraper/src
# change access token to your own (https://developers.facebook.com/tools/explorer/)
access_token="EAACEdEose0cBAO5BprvNk6JLcZBPkR9VreibSZBEZCZCDyKBcXdH9DkDJsx7c5tflMGx2Q698QZCfZCqih3WMS9jFjf0nG5Oy6mVzZABsQ167mC19ow0gJdK1GFIpOJGKoXUCiIdhZBWf2579fVf8JK8jZCJ34DxZB4AynQX29G1Td2wZDZD"
# change ID's if you want to scrape other Facebook pages
ID_list="127167520968693 76748198685 513643295475511"

## scrape sample Facebook pages to separate SQlite databases
for id in $ID_list
do
	python scrapeFB.py -a $access_token -d ../example/$id.sqlite -i $id
done

