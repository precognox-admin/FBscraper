#!/usr/bin/env python
# -*-coding:utf-8-*-

# import necessary Python libraries
import simplejson
import facebook
import hashlib
import sys
import sqlite3 as lite
from datetime import datetime

if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib import urlopen


class Scraper:
    def __init__(self, access_token, db_path, id_list):
        """Connects to Facebook Graph API and creates an SQLite database with four tables for Posts, Comments,
        Post_likes and People if not exists.

        Takes three arguments:
        access_token: your own Facebook access token that you can get on https://developers.facebook.com/tools/explorer/
        db_path: the path of the SQLite database where you want to store the data
        id_list: ID's of the Facebook pages you want to scrape
        """
        self.access_token = access_token
        self.db_path = db_path
        self.id_list = id_list

        g = facebook.GraphAPI(self.access_token)
        self.g = g

        # connect to database
        con = lite.connect(self.db_path)
        self.con = con

        with con:
            # create cursor to the database
            cur = con.cursor()
            self.cur = cur
            # create tables for posts, comments, post likes and people if not exists
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Posts(message_id TEXT PRIMARY KEY, content TEXT, author_hash_id TEXT, "
                "link TEXT, location TEXT, published_date TEXT, date_inserted TEXT, last_comment TEXT, "
                "status_id TEXT, status_link TEXT, message_type TEXT, status_type TEXT, video_source TEXT, "
                "picture_link TEXT, link_name TEXT, link_caption TEXT, link_description TEXT, num_mentions INTEGER, "
                "mentions TEXT, like_count INTEGER, comment_count INTEGER, share_count INTEGER)")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Comments(comment_id TEXT PRIMARY KEY, message_id TEXT, "
                "comment_content TEXT, author_hash_id TEXT, comment_date TEXT, like_count INTEGER)")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Post_likes(like_id TEXT PRIMARY KEY, author_hash_id TEXT, message_id TEXT)")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS People(author_hash_id TEXT PRIMARY KEY, author_id TEXT, author_name TEXT)")

    def write_data(self, d):
        """Writes data from the given Facebook page in SQLite database separated in four tables for posts, comments,
        likes and people. Takes the converted JSON of a Facebook page from given feed as argument."""

        date_inserted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messages = d['data']
        self.no_messages += len(messages)

        for message in messages:

            author_name = message['from']['name']
            author_id = message['from']['id']
            author_hash_id = hashlib.md5(author_id.encode('utf-8')).hexdigest()
            published_date = message['created_time']
            published_date = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S+%f").strftime("%Y-%m-%d %H:%M:%S")
            message_type = message['type']
            message_id = message['id']
            org_id = message_id.split('_')[0]
            status_id = message_id.split('_')[1]
            status_link = 'https://www.facebook.com/%s/posts/%s' % (org_id, status_id)

            if 'place' in message:
                location = str(message['place'])
            else:
                location = ''

            if 'link' in message:
                link = message['link']
            else:
                link = ''

            if 'name' in message:
                link_name = message['name']
            else:
                link_name = ''

            if 'caption' in message:
                link_caption = message['caption']
            else:
                link_caption = ''

            if 'description' in message:
                link_description = message['description']
            else:
                link_description = ''

            if 'message' in message:
                content = message['message']
                content = content.replace('\n', '')
            else:
                content = ''

            if 'status_type' in message:
                status_type = message['status_type']
            else:
                status_type = ''

            if 'picture' in message:
                picture_link = message['picture']
            else:
                picture_link = ''

            if 'source' in message:
                video_source = message['source']
            else:
                video_source = ''

            comment_count = 0
            comment_dates = [published_date]
            if 'comments' in message:
                for each_comment in message['comments']['data']:
                    comment_content = each_comment['message']
                    comment_id = each_comment['id']
                    comment_author = each_comment['from']
                    comment_author_id = comment_author['id']
                    comment_author_hash_id = hashlib.md5(comment_author_id.encode('utf-8')).hexdigest()
                    comment_author_name = comment_author['name']
                    comment_created = each_comment['created_time']
                    comment_created = datetime.strptime(comment_created, "%Y-%m-%dT%H:%M:%S+%f").strftime(
                        "%Y-%m-%d %H:%M:%S")
                    comment_dates.append(comment_created)
                    like_count = str(each_comment['like_count'])
                    if len(like_count) < 1:
                        like_count = '0'
                    comments_data = (comment_id, message_id, comment_content, comment_author_hash_id, comment_created,
                                     like_count)
                    people_data = (comment_author_hash_id, comment_author_id, comment_author_name)
                    self.cur.execute("INSERT OR IGNORE INTO Comments VALUES(?, ?, ?, ?, ?, ?)", comments_data)
                    self.cur.execute(
                        "UPDATE Comments SET like_count=like_count WHERE CHANGES()=0 AND comment_id=comment_id")
                    self.cur.execute("INSERT OR IGNORE INTO People VALUES(?, ?, ?)", people_data)
                    comment_count += 1

                    if 'next' in message['comments']['paging']:
                        next_comment_url = message['comments']['paging']['next']
                        while next_comment_url:
                            try:
                                with urlopen(next_comment_url) as url:
                                    s = url.read()
                                get_more_comment = simplejson.loads(s)
                                for more_comments in get_more_comment['data']:
                                    comment_content = more_comments['message']
                                    comment_id = more_comments['id']
                                    comment_author = more_comments['from']
                                    comment_author_id = comment_author['id']
                                    comment_author_hash_id = hashlib.md5(
                                        comment_author_id.encode('utf-8')).hexdigest()
                                    comment_author_name = comment_author['name']
                                    comment_created = more_comments['created_time']
                                    comment_created = datetime.strptime(
                                        comment_created, "%Y-%m-%dT%H:%M:%S+%f").strftime("%Y-%m-%d %H:%M:%S")
                                    comment_dates.append(comment_created)
                                    like_count = str(more_comments['like_count'])
                                    if len(like_count) < 1:
                                        like_count = '0'
                                    comments_data = (
                                        comment_id, message_id, comment_content, comment_author_hash_id,
                                        comment_created, like_count)
                                    people_data = (comment_author_hash_id, comment_author_id, comment_author_name)
                                    self.cur.execute("INSERT OR IGNORE INTO Comments VALUES(?, ?, ?, ?, ?, ?)",
                                                     comments_data)
                                    self.cur.execute("UPDATE Comments SET like_count=like_count "
                                                     "WHERE CHANGES()=0 AND comment_id=comment_id")
                                    self.cur.execute("INSERT OR IGNORE INTO People VALUES(?, ?, ?)", people_data)
                                    comment_count += 1

                            except Exception as e:
                                print("Error reading", e)
                                break

                            if 'paging' in get_more_comment:
                                if 'next' in get_more_comment['paging']:
                                    next_comment_url = get_more_comment['paging']['next']
                                else:
                                    break

            num_mentions = 0
            if 'to' in message:
                num_mentions = len(message['to']['data'])
                if num_mentions != 0:
                    mentions_list = [i['name'] for i in message['to']['data'] if 'name' in i]
                else:
                    mentions_list = ''
                mentions = ', '.join(mentions_list)
            else:
                mentions = ''

            if 'shares' in message:
                share_count = message['shares']['count']
            else:
                share_count = 0

            like_count = 0
            likers = {}
            if 'likes' in message:
                l = self.g.get_object(message['id'])['likes']
                like_count = len(l['data'])
                for k in l['data']:
                    likers[k['id']] = k['name']
                if 'paging' in l.keys():
                    while True:
                        try:
                            with urlopen(l['paging']['next']) as url:
                                s = url.read()
                            l = simplejson.loads(s)
                            like_count += len(l['data'])
                            for k in l['data']:
                                likers[k['id']] = k['name']
                        except:
                            break

                for k in likers.keys():
                    liker_id = k
                    liker_hash_id = hashlib.md5(liker_id.encode('utf-8')).hexdigest()
                    liker_name = likers[k]
                    like_id = message_id + '_' + liker_hash_id
                    likes_data = (like_id, liker_hash_id, message_id)
                    people_like_data = (liker_hash_id, liker_id, liker_name)
                    self.cur.execute("INSERT OR IGNORE INTO Post_likes VALUES(?, ?, ?)", likes_data)
                    self.cur.execute("INSERT OR IGNORE INTO People VALUES(?, ?, ?)", people_like_data)

            last_comment = max(comment_dates)
            post_data = (
                message_id, content, author_hash_id, link, location, published_date, date_inserted, last_comment,
                status_id, status_link, message_type, status_type, video_source, picture_link, link_name, link_caption,
                link_description, num_mentions, mentions, like_count, comment_count, share_count)
            people_org_data = (author_hash_id, author_id, author_name)
            self.cur.execute(
                "INSERT OR IGNORE INTO Posts VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                post_data)
            self.cur.execute(
                "UPDATE Posts SET last_comment=last_comment, num_mentions=num_mentions, mentions=mentions, "
                "like_count=like_count, comment_count=comment_count, "
                "share_count=share_count WHERE CHANGES()=0 AND message_id=message_id")
            self.cur.execute("INSERT OR IGNORE INTO People VALUES(?, ?, ?)", people_org_data)
            self.con.commit()

    def scrape(self):
        """Scrapes the pages from the feed of the given Facebook ID's. Performs the paging, reads the JSON's from the
        page URL's and writes data in new or existing SQLite database. Uses method write.data."""

        for feed in self.id_list:

            try:
                d = self.g.get_connections(feed, 'feed')
            except Exception as e:
                print("Error reading feed id %s, exception: %s" % (feed, e))
                continue

            no_messages = 0
            self.no_messages = no_messages
            count = 1
            print("Scraping page %s of feed id %s" % (count, feed))
            self.write_data(d)

            try:
                paging = d['paging']
                if 'next' in paging:
                    next_page_url = paging['next']

                while next_page_url:

                    count += 1
                    print("Scraping page %s" % count)

                    try:
                        # convert json into nested dicts and lists
                        with urlopen(next_page_url) as url:
                            s = url.read()
                        d = simplejson.loads(s)
                    except Exception as e:
                        print("Error reading id %s, exception: %s" % (feed, e))
                        continue

                    if len(d['data']) == 0:
                        print("There aren't any other messages.")
                        break

                    self.write_data(d)

                    if 'paging' in d:
                        if 'next' in d['paging']:
                            next_page_url = d['paging']['next']
                        else:
                            break

            except Exception as e:
                if self.no_messages > 0:
                    print(
                        "There aren't any other pages. Scraping of feed id %s is done! "
                        "There were %s messages to scrape." % (feed, self.no_messages))
                else:
                    print("There is nothing to scrape. Perhaps the id you provided is a personal page.")
                continue

        self.con.close()


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--access_token',
        help='you can get your own Facebook access token on https://developers.facebook.com/tools/explorer/')
    parser.add_argument('-d', '--db_path', help='the path of the SQLite database where you want to store the data')
    parser.add_argument('-i', '--id_list', nargs='+', help="the ID's of the Facebook pages you want to scrape")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        args.access_token = input('Please type your own Facebook access token: ')
        args.db_path = input('Please type the path of the SQLite database where you want to store the data: ')
        args.id_list = input("Please type the ID's of the Facebook pages you want to scrape: ")

    s = Scraper(args.access_token, args.db_path, args.id_list)
    s.scrape()
