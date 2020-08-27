# provides the main class "Newsboat" and
# the namedtuples "Item", "FeedData", "FeedConfigs" and "Feed"

import sqlite3                      # to access the cache database of newsboat
import re                           # to perform some regex on config files
from collections import namedtuple  # to have a lightweight class replacement
import os.path                      # to check if files/directories exist
from subprocess import DEVNULL, STDOUT, check_call # to make newsboat reload

# Namedtuples for handeling rss feeds and rss items better
# Structured the same as in the cache.db of newsboat -> without user config

# Items are straight forward: they incoroprate every property of the database
# rss items.
Item = namedtuple('Item', 'id guid title author url feedurl pubDate content \
                           unread enclosure_url enclosure_type enqueued flags \
                           deleted base')
# Feeds are a bit more complicated. In that design I split them into:
# FeedData (incoroprates all property of one row in rss_feed database)
# FeedConfigs (has alias and tags of feeds which can be read from configfile)
FeedData = namedtuple('FeedData', 'rssurl url title lastmodified is_rtl etag')
FeedConfigs = namedtuple('FeedConfigs', 'alias tags')
# The enduser will only see/use the feed object which is what you get when merging
# a feeddata and a feedconfigs.
# Merging happens like that: feedObj = Feed(*(dataFeedObj+configsFeedObj))
# https://stackoverflow.com/questions/12161649/what-is-the-simple-way-to-merge-named-tuples-in-python
Feed = namedtuple('Feed','rssurl url title lastmodified is_rtl etag alias tags')

# The main class
class Newsboat:
    def __init__(self, path_to_config=None, path_to_db=None):

        if path_to_config is None:
            self.path_to_config = os.getenv("HOME") + "/.config/newsboat"
        else:
            self.path_to_config = path_to_config

        if path_to_db is None:
            self.path_to_db = os.getenv("HOME") + "/.local/share/newsboat/cache.db"
        else:
            self.path_to_db = path_to_db

        if not os.path.exists(self.path_to_config):
            raise FileExistsError("Couldn't find your config file. Consider to \
 specify the path when initalizing the Newsboat class: \
 Newsboat(path_to_config='/path/to/config/directory')")

        if not os.path.exists(self.path_to_db):
            raise FileExistsError("Couldn't find your database file. Consider to \
 specify the path when initalizing the Newsboat class: \
 Newsboat(path_to_db='/path/to/config/database.db)")

        # initalize feeds and tags
        self.__data_feeds = self.__get_all_feed_data()
        self.feeds = [self.__get_feed(feed) for feed in self.__data_feeds]
        self.tags = []
        for conf_feed in self.feeds:
            for tag in conf_feed.tags:
                if tag not in self.tags:
                    self.tags.append(tag)

    def __repr__(self):
        return f'<Newsboat object>'

    @staticmethod
    def update():
        check_call(['newsboat', '--execute=reload'], stdout=DEVNULL,
                    stderr=STDOUT)

    @staticmethod
    def __sqlite_fetch_to_item(sqlite_fetch):
        # takes the unorganized tuple/row of a fetch in the 'rss_item' table
        # and returns the corresponding Item obj
        item = sqlite_fetch
        temp_item = Item(id=item[0], guid=item[1], title=item[2],
                        author=item[3], url=item[4], feedurl=item[5],
                        pubDate=item[6], content=item[7], unread=item[8],
                        enclosure_url=item[9], enclosure_type=item[10],
                        enqueued=item[11], flags=item[12], deleted=item[13],
                        base=item[14])
        return temp_item

    @staticmethod
    def __sqlite_fetch_to_data_feed(sqlite_fetch):
        # takes the unorganized tuple/row of a fetch in the 'rss_feed' table
        # and returns the corresponding FeedData obj
        temp = sqlite_fetch
        temp_feed = FeedData(rssurl=temp[0], url=temp[1], title=temp[2],
                        lastmodified=temp[3], is_rtl=temp[4], etag=temp[5])
        return temp_feed

    def __cursor_db(self):
        return sqlite3.connect(self.path_to_db).cursor()

    def __get_feed(self, data_feed_obj):
        # takes a FeedData obj and returns a Feed obj
        # to do that it accesses the config file
        with open(self.path_to_config + "/urls", "r") as configfile:
            config_lines = configfile.readlines()
            for line in config_lines:
                if data_feed_obj.rssurl in line:
                    feed_alias = re.findall('"~([^"]+)', line)
                    tags = [tag for tag in re.findall('"(.*?)"', line)
                            if tag[0] != "~"]
                    if feed_alias:
                        configured_feed_obj = FeedConfigs(feed_alias[0], tags)
                    else:
                        configured_feed_obj = FeedConfigs(data_feed_obj, None, tags)
                    feed = Feed(*(data_feed_obj+configured_feed_obj))
                    return feed
            else:
                raise Exception(f'Could not read anything from the config file in "{self.path_to_config}"')

    def __get_all_feed_data(self):
        # returns all feeds in the rss_feed table as array of FeedData obj
        cur = self.__cursor_db()
        cur.execute(f"SELECT * FROM 'rss_feed';")
        all_feeds_data = []
        for obj in cur.fetchall():
            temp_feed = self.__sqlite_fetch_to_data_feed(obj)
            all_feeds_data.append(temp_feed)
        return all_feeds_data

    def get_all_unread_items(self):
        # returns all unread items
        cur = self.__cursor_db() # access cache
        cur.execute(f"SELECT * FROM 'rss_item' WHERE unread IS 1;")
        result_item_array = []
        for obj in cur.fetchall():
            temp_item = self.__sqlite_fetch_to_item(obj)
            result_item_array.append(temp_item)
        return result_item_array

    def get_all_items_from_defined_feed(self, feed_obj):
        rssurl = feed_obj.rssurl
        cur = self.__cursor_db()
        cur.execute(f"SELECT * FROM 'rss_item' WHERE feedurl='{rssurl}'")
        result_item_array = []
        for item in cur.fetchall():
            temp_item = self.__sqlite_fetch_to_item(item)
            result_item_array.append(temp_item)
        return result_item_array
