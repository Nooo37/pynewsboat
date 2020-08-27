# pynewsboat
A small python module to access the local newsboat database and config file.

## Quickstart
Place the directory `pynewsboat` in the same directory as your python script that should access the module.
Your directory structure should look roughly like that:
```bash
your_dir
├── your_script.py
└── pynewsboat
    ├── __init__.py
    └── newsboat.py
```
To access all functions of that module, you can import and initalize the `Newsboat` class in `your_script.py` like that:
```python
from pynewsboat import Newsboat

my_newsboat = Newsboat()
```

## Usage

### The Newsboat class
The `Newsboat` class has two properties:
- `feeds` provides an array of all Feed objects from the database
- `tags` provides an array of all tags as strings from the configuration file

Furthermore, the `Newsboat` class has the following methods:
- `update()` which updates the newsboat instance
- `get_all_unread_items()` which returns an array of `Item`s that are marked as unread in the database
- `get_all_items_from_defined_feed(feed_obj)` which takes a `Feed` as an argument and returns all `Items` of that feed from the database

### Feeds and Items
Each feed and each item that you get your hands on is a `namedtuple` with the following properties:
- `Feed`: `rssurl`, `url`, `title`, `lastmodified`, `is_rtl`, `etag`, `alias`, `tags`
- `Item`: `id`, `guid`, `title`, `author`, `url`, `feedurl`, `pubDate`, `content`, `unread`, `enclosure_url`, `enclosure_type`, `enqueued flags`, `deleted base`

Properties can therefore easily be called as if they were classes. For example: `some_item.content` would return the content of the Item `some_item`.

Be aware that some of those properties are often empty since it's always the choice of the RSS feeds owner to provide these information.

## Contributions
Contributions to that module are always welcomed.
