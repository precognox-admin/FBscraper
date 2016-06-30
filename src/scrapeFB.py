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

        g = facebook.GraphAPI(self.access_token, version='2.3')
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
                "CREATE TABLE IF NOT EXISTS Posts(post_id TEXT PRIMARY KEY, status_id TEXT, content TEXT, "
                "person_hash_id TEXT, published_date TEXT, last_comment_date TEXT, post_type TEXT, status_type TEXT, "
                "post_link TEXT, link TEXT, video_link TEXT, picture_link TEXT, link_name TEXT, link_caption TEXT, "
                "link_description TEXT, comment_count INTEGER, share_count INTEGER, like_count INTEGER, "
                "love_count INTEGER, wow_count INTEGER, haha_count INTEGER, sad_count INTEGER, angry_count INTEGER, "
                "mentions_count INTEGER, mentions TEXT, location TEXT, date_inserted TEXT)")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Comments(comment_id TEXT PRIMARY KEY, person_hash_id TEXT, post_id TEXT, "
                "comment_content TEXT, comment_date TEXT, like_count INTEGER)")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS Post_likes(like_id TEXT PRIMARY KEY, person_hash_id TEXT, post_id TEXT)")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS People(person_hash_id TEXT PRIMARY KEY, person_id TEXT, person_name TEXT)")

    def get_reactions(self, post_id, access_token):
        """Gets reactions for a post."""

        base = "https://graph.facebook.com/v2.6"
        node = "/%s" % post_id
        reactions = "/?fields=" \
                    "reactions.type(LIKE).limit(0).summary(total_count).as(like)," \
                    "reactions.type(LOVE).limit(0).summary(total_count).as(love)," \
                    "reactions.type(WOW).limit(0).summary(total_count).as(wow)," \
                    "reactions.type(HAHA).limit(0).summary(total_count).as(haha)," \
                    "reactions.type(SAD).limit(0).summary(total_count).as(sad)," \
                    "reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
        parameters = "&access_token=%s" % access_token
        url = base + node + reactions + parameters

        # retrieve data
        with urlopen(url) as url:
            read_url = url.read()
        data = simplejson.loads(read_url)

        return data

    def write_data(self, d):
        """Writes data from the given Facebook page in SQLite database separated in four tables for posts, comments,
        likes and people. Takes the converted JSON of a Facebook page from given feed as argument."""

        date_inserted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messages = d['data']
        self.no_messages += len(messages)

        for message in messages:

            person_name = message['from']['name']
            person_id = message['from']['id']
            person_hash_id = hashlib.md5(person_id.encode('utf-8')).hexdigest()
            published_date = message['created_time']
            published_date = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S+%f").strftime("%Y-%m-%d %H:%M:%S")
            post_type = message['type']
            post_id = message['id']
            org_id = post_id.split('_')[0]
            status_id = post_id.split('_')[1]
            post_link = 'https://www.facebook.com/%s/posts/%s' % (org_id, status_id)

            location = '' if 'place' not in message else str(message['place'])
            link = '' if 'link' not in message else str(message['link'])
            link_name = '' if 'name' not in message else message['name']
            link_caption = '' if 'caption' not in message else message['caption']
            link_description = '' if 'description' not in message else message['description']
            content = '' if 'message' not in message else message['message'].replace('\n', ' ')
            status_type = '' if 'status_type' not in message else message['status_type']
            picture_link = '' if 'picture' not in message else message['picture']
            video_link = '' if 'source' not in message else message['source']
            share_count = 0 if 'shares' not in message else message['shares']['count']

            reaction_data = self.get_reactions(post_id=post_id, access_token=self.access_token) \
                if published_date > '2016-02-24 00:00:00' else {}
            love_count = 0 if 'love' not in reaction_data else reaction_data['love']['summary']['total_count']
            wow_count = 0 if 'wow' not in reaction_data else reaction_data['wow']['summary']['total_count']
            haha_count = 0 if 'haha' not in reaction_data else reaction_data['haha']['summary']['total_count']
            sad_count = 0 if 'sad' not in reaction_data else reaction_data['sad']['summary']['total_count']
            angry_count = 0 if 'angry' not in reaction_data else reaction_data['angry']['summary']['total_count']
            reaction_like_count = 0 if 'like' not in reaction_data else reaction_data['like']['summary']['total_count']

            mentions_count = 0
            if 'to' in message:
                mentions_count = len(message['to']['data'])
                mentions_list = '' if mentions_count != 0 else [i['name'] for i in message['to']['data'] if 'name' in i]
                mentions = ', '.join(mentions_list)
            else:
                mentions = ''

            comment_count = 0
            comment_dates = [published_date]
            if 'comments' in message:
                for each_comment in message['comments']['data']:
                    comment_content = each_comment['message']
                    comment_id = each_comment['id']
                    comment_author = each_comment['from']
                    comment_person_id = comment_author['id']
                    comment_person_hash_id = hashlib.md5(comment_person_id.encode('utf-8')).hexdigest()
                    comment_person_name = comment_author['name']
                    comment_created = each_comment['created_time']
                    comment_created = datetime.strptime(comment_created, "%Y-%m-%dT%H:%M:%S+%f").strftime(
                        "%Y-%m-%d %H:%M:%S")
                    comment_dates.append(comment_created)
                    like_count = str(each_comment['like_count'])
                    if len(like_count) < 1:
                        like_count = '0'
                    comments_data = (comment_id, comment_person_hash_id, post_id, comment_content, comment_created,
                                     like_count)
                    people_data = (comment_person_hash_id, comment_person_id, comment_person_name)
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
                                    read_url = url.read()
                                get_more_comment = simplejson.loads(read_url)
                                for more_comments in get_more_comment['data']:
                                    comment_content = more_comments['message']
                                    comment_id = more_comments['id']
                                    comment_author = more_comments['from']
                                    comment_person_id = comment_author['id']
                                    comment_person_hash_id = hashlib.md5(
                                        comment_person_id.encode('utf-8')).hexdigest()
                                    comment_person_name = comment_author['name']
                                    comment_created = more_comments['created_time']
                                    comment_created = datetime.strptime(
                                        comment_created, "%Y-%m-%dT%H:%M:%S+%f").strftime("%Y-%m-%d %H:%M:%S")
                                    comment_dates.append(comment_created)
                                    like_count = str(more_comments['like_count'])
                                    if len(like_count) < 1:
                                        like_count = '0'
                                    comments_data = (
                                        comment_id, comment_person_hash_id, post_id, comment_content,
                                        comment_created, like_count)
                                    people_data = (comment_person_hash_id, comment_person_id, comment_person_name)
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
            last_comment_date = max(comment_dates)

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
                                read_url = url.read()
                            l = simplejson.loads(read_url)
                            like_count += len(l['data'])
                            for k in l['data']:
                                likers[k['id']] = k['name']
                        except:
                            break

                for k in likers.keys():
                    liker_id = k
                    liker_hash_id = hashlib.md5(liker_id.encode('utf-8')).hexdigest()
                    liker_name = likers[k]
                    like_id = post_id + '_' + liker_hash_id
                    likes_data = (like_id, liker_hash_id, post_id)
                    people_like_data = (liker_hash_id, liker_id, liker_name)
                    self.cur.execute("INSERT OR IGNORE INTO Post_likes VALUES(?, ?, ?)", likes_data)
                    self.cur.execute("INSERT OR IGNORE INTO People VALUES(?, ?, ?)", people_like_data)

            like_count = like_count if published_date < '2016-02-24 00:00:00' else reaction_like_count

            post_data = (
                post_id, status_id, content, person_hash_id, published_date, last_comment_date, post_type, status_type,
                post_link, link, video_link, picture_link, link_name, link_caption, link_description, comment_count,
                share_count, like_count, love_count, wow_count, haha_count, sad_count, angry_count, mentions,
                mentions_count, location, date_inserted)
            people_org_data = (person_hash_id, person_id, person_name)
            self.cur.execute(
                "INSERT OR IGNORE INTO Posts VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "?, ?, ?, ?, ?)",
                post_data)
            self.cur.execute(
                "UPDATE Posts SET last_comment_date=last_comment_date, mentions_count=mentions_count, "
                "mentions=mentions, like_count=like_count, comment_count=comment_count, "
                "share_count=share_count WHERE CHANGES()=0 AND post_id=post_id")
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
                            read_url = url.read()
                        d = simplejson.loads(read_url)
                    except Exception as e:
                        print("Error reading id %s, exception: %s" % (feed, e))
                        continue

                    if len(d['data']) == 0:
                        print("There aren't any other posts. Scraping of feed id %s is done! " % feed)
                        break

                    self.write_data(d)

                    if 'paging' in d:
                        if 'next' in d['paging']:
                            next_page_url = d['paging']['next']
                        else:
                            break

            except:
                if self.no_messages > 0:
                    print("There aren't any other pages. Scraping of feed id %s is done! " % feed)
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
