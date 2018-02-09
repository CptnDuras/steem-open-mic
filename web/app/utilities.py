import json
import math
import traceback
from datetime import timedelta

import bleach
import markdown
import pandas as pd
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from web.app.config import SQLALCHEMY_DATABASE_URI
from web.app.models import *

# compile regex for checking for youtube videos
youtube_video_regex = '((\n.{0,3})|(src\s?=\s?.{1}))((http(s)?://youtu.be/)|(http(s)?://www.youtube.com/embed/)|(http(s)?://www.youtube.com/)|(http(s)?://m.youtube.com/))(watch\?v=)?(?P<videoid>(\w|\_|\-)+)'
youtube_video_regex = re.compile(youtube_video_regex)


def log(s):
    with open('monitor-log.txt', 'a') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ', ')
        f.write(str(s) + '\n')


def get_payout_string(payout):
    return "${:.2f}".format(payout)


# todo - add weeks, months and years
def get_age_string(dt):
    """
    Get the age of a post
    :param DateTime dt: Post time
    :return str: String of date
    """

    timediff = datetime.now() - dt

    if timediff < timedelta(minutes=2):
        return '{0:.0f} minute ago'.format(math.floor(timediff.seconds / 60))
    elif timediff < timedelta(hours=1):
        return '{0:.0f} minutes ago'.format(math.floor(timediff.seconds / 60))
    elif timediff < timedelta(hours=2):
        return '1 hour ago'
    if timediff < timedelta(days=1):
        return '{0:.0f} hours ago'.format(math.floor(timediff.seconds / 3600))
    elif timediff < timedelta(days=2):
        return '1 day ago'
    elif timediff < timedelta(days=365):
        return '{0:.0f} days ago'.format(math.floor(timediff.days))
    else:
        return '{0:.0f} years ago'.format(math.floor(timediff.days / 365))


def get_duration_string(seconds):
    """
    Get a string representation of the duration from seconds
    :param float seconds:
    :return str:
    """
    # noinspection PyBroadException
    try:
        if seconds > 0:
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            if h > 0:
                return "%d:%02d:%02d" % (h, m, s)
            else:
                return "%d:%02d" % (m, s)
        else:
            return ''
    except Exception as ex:
        log(f"{ex}\n{traceback.format_exc()}")
        return ''  # duration not available


# todo - improve efficiency of this
# noinspection PyBroadException
def markdown_to_safe_html(s):
    """

    :param s:
    :return:
    """
    html = s
    try:
        # Get HTML, and replace newlines with break tags
        html = html.replace('\n', '<br>')
        # Convert html to markdown
        html = markdown.markdown(html)
    except Exception as ex:
        log(f"Problem converting markdown to html: {ex}\n{traceback.format_exc()}")

    try:
        # remove scripts/images
        html = bleach.clean(
            html,
            tags=['br', 'b', 'i', 'pre', 'code', 'table', 'a'],
            strip=True
        )
    except Exception as ex:
        log(f"Problem removing unwanted html elements: {ex}\n{traceback.format_exc()}")

    try:
        # Linkify bleached html
        html = bleach.linkify(html)
    except Exception as ex:
        log(f"Problem adding links: {ex}\n{traceback.format_exc()}")

    # remove unwanted blank lines
    while "<br><br><br>" in html:
        html = html.replace('<br><br><br>', '<br><br>')

    return html


# noinspection PyBroadException
def get_valid_video(comment):
    """
    Get valid video
    :param comment:
    :return str, str, str: Source, video ID, category
    """
    try:
        body = comment['body']
        if body[:2] == '@@':
            return None, None, None
    except Exception as ex:
        log(f"Error: No valid body html/markdown in comment: {comment['author']}/{comment['permlink']}")
        log(f"Problem adding links: {ex}\n{traceback.format_exc()}")
        return None, None, None

    js = comment.get('json_metadata', '[]')
    try:
        metadata = json.loads(js)
    except Exception as ex:
        log('Error: No valid json_metadata for comment: ' + comment['author'] + '/' + comment['permlink'])
        log(f"Problem adding links: {ex}\n{traceback.format_exc()}")
        return None, None, None

    category = comment.get('category', '')

    if not category:
        try:
            category = ", ".join(metadata['tags'])
        except Exception as ex:
            log(f"Problem getting metadata: {ex}\n{traceback.format_exc()}")
            return None, None, None

    # if it's not openmic. Die
    if "openmic" not in category.split(", "):
        return None, None, None
    else:
        log("Found openmic")

    # see if it's a dlive video
    try:
        if metadata['app'].find('dlive') >= 0:
            log('DLive post detected...')
            video_id = metadata.get('ipfsHash', 'live')  # will initially be marked as live, then get hash once finished
            if video_id:
                log('DLive post returned - ' + str(video_id))
                return 'dlive', video_id, category
    except Exception as ex:
        log(f"{ex}\n{traceback.format_exc()}")

    # see if it's a dtube video, and use 480 version if available - todo - store both hashs?
    try:
        # sometimes dtube video are shown with app: steemit
        if metadata['app'].find('dtube') >= 0 or comment['parent_permlink'] == 'dtube':
            content = metadata['video']['content']
            video_id = content.get('videohash', '')
            video_id = content.get('video480hash', video_id)
            if video_id:
                return 'dtube', video_id, category
    except Exception as ex:
        log(f"{ex}\n{traceback.format_exc()}")

    # get youtube video (if only 1 is embedded in post body)
    # todo - check regex will collect all videos, possibly use bs instead of regex for parsing
    # todo - better handle posts with more than 1 video
    try:
        matches = [m.groupdict() for m in youtube_video_regex.finditer(body)]
        if len(matches) == 1:
            media_id = matches[0]['videoid']
        else:
            media_id = None

        excluded_ids = ["channel", "edit", "watch", "c", "user", "playlist", None]
        if media_id not in excluded_ids:  # exclude invalid video ids
            log('YouTube Video: ' + media_id)  # for debugging regex
            return 'youtube', media_id, category
    except Exception as ex:
        log(f"{ex}\n{traceback.format_exc()}")

    return None, None, None


# noinspection PyBroadException
def seconds_from_youtube_duration(durationstring):
    match = re.search('PT((?P<hours>\d{1,2})H)?((?P<minutes>\d{1,2})M)?((?P<seconds>\d{1,2})S)?', durationstring)
    try:
        hours = int(match.group('hours'))
    except Exception as ex:
        hours = 0
        log(f"{ex}\n{traceback.format_exc()}")

    try:
        minutes = int(match.group('minutes'))
    except Exception as ex:
        minutes = 0
        log(f"{ex}\n{traceback.format_exc()}")

    try:
        seconds = int(match.group('seconds'))
    except Exception as ex:
        seconds = 0
        log(f"{ex}\n{traceback.format_exc()}")

    return hours * 3600 + minutes * 60 + seconds


# experimentally get urls for image resizing proxy
# todo - check scalability of this kind of approach, investigate other service providers (eg. tiny.pictures)
def resized_image_url_from_url(url, width=280, height=157):
    url = url.replace('http://', '').replace('https://', '')
    newurl = 'https://images.weserv.nl/?url=' + url + '&w=' + str(width) + '&h=' + str(height) + '&t=letterbox&bg=black'
    return newurl


def get_sparkline_data_from_content(steem_post_content):
    data = steem_post_content['active_votes']
    data.append(
        {'time': steem_post_content['created'], 'rshares': 0, 'voter': '', 'weight': 0, 'percent': 0, 'reputation': 0})
    data.append(
        {'time': datetime.now().strftime('%Y-%m-%-dT%H:%M:%S'), 'rshares': 0, 'voter': '', 'weight': 0, 'percent': 0,
         'reputation': 0})
    df = pd.DataFrame(data)
    df['rshares'] = df['rshares'].apply(int)
    times = pd.to_datetime(df['time'])
    df['interval'] = ((times.astype(pd.np.int64) / 10 ** 9) / 60).astype(pd.np.int64)  # one minute interval
    df = df[['interval', 'rshares']]
    dd = []
    mins = 0

    for t in range(df['interval'].min(), df['interval'].max()):
        dd.append({'interval': t, 'rshares': 0})
        mins += 1
        if mins > 10080:  # limit to one week of votes
            break
    # Todo: figure out why this inspection doesn't work
    # noinspection PyTypeChecker
    df2 = pd.DataFrame(dd)
    df = df.append(df2)
    df = df.sort_values(['interval'])

    # group into 20 bins for sparkline values
    bins = pd.np.linspace(df.interval.min(), df.interval.max(), 20)
    df = df.groupby(pd.np.digitize(df.interval, bins))['rshares'].sum()
    df = df.cumsum()

    return str([0] + df.tolist())


def get_voters_list_from_content(steem_post_content):
    data = steem_post_content['active_votes']
    return [x['voter'] for x in data]



def create_video_summary_fields(df, filter_data={}):
    # temporary fix dlive thumbnails to https to prevent SSL warning
    #    df = df[~(df['video_thumbnail_image_url']==None)]
    df['video_thumbnail_image_url'] = df['video_thumbnail_image_url'].apply(
        lambda x: x.replace('http://', 'https://') if x != None else '')

    df = df[~pd.isnull(df['created'])]
    df = df[~(df['video_id'] == 'c')]  # remove erroneous records todo - remove once db refreshed
    df = df[~(df['video_id'] == 'user')]  # remove erroneous records todo - remove once db refreshed
    df['duration_string'] = df['video_duration_seconds'].apply(get_duration_string)
    df['age_string'] = df['created'].apply(get_age_string)
    df['video_post_delay_days'] = df['video_post_publish_delay_seconds'] // (3600 * 24)

    df['payout_string'] = (df['pending_payout_value'] + df['total_payout_value']).apply(lambda x: get_payout_string(x))
    df['title'] = df['title'].apply(lambda x: markdown_to_safe_html(x))
    df['title_truncated'] = df['title'].apply(lambda x: x[:80])

    # experimental resizing through free image proxy/cache
    df['video_thumbnail_image_url'] = df['video_thumbnail_image_url'].apply(lambda x: resized_image_url_from_url(x))

    return df[['author', 'permlink', 'category', 'title', 'title_truncated', 'created', 'age_string', 'payout_string',
               'duration_string', 'video_type', 'video_id', 'video_thumbnail_image_url', 'video_post_delay_days',
               'trending_score', 'hot_score', 'votes_sparkline_data']]


# appends the query dict (from json filter data) to existing query
def apply_filter_to_query(original_query, filter_data):
    new_query = original_query
    if filter_data.get('filter_age_selection', 'all') == 'hour':
        new_query = new_query.filter(Post.created > (datetime.now() - timedelta(hours=1)))
    elif filter_data.get('filter_age_selection', 'all') == 'today':
        new_query = new_query.filter(Post.created > (datetime.now() - timedelta(hours=24)))
    elif filter_data.get('filter_age_selection', 'all') == 'week':
        new_query = new_query.filter(Post.created > (datetime.now() - timedelta(days=7)))
    elif filter_data.get('filter_age_selection', 'all') == 'month':
        new_query = new_query.filter(Post.created > (datetime.now() - timedelta(days=30)))
    if filter_data.get('filter_type_selection', 'all') == 'youtube':
        new_query = new_query.filter(Post.video_type == 'youtube')
    elif filter_data.get('filter_type_selection', 'all') == 'dtube':
        new_query = new_query.filter(Post.video_type == 'dtube')
    elif filter_data.get('filter_type_selection', 'all') == 'dlive':
        new_query = new_query.filter(Post.video_type == 'dlive')
    if filter_data.get('filter_duration_selection', 'all') == 'short':
        new_query = new_query.filter(Post.video_duration_seconds <= 240)
    elif filter_data.get('filter_duration_selection', 'all') == 'long':
        new_query = new_query.filter(Post.video_duration_seconds > 1200)
    if filter_data.get('filter_exclude_old_video', 'false') == 'true':
        new_query = new_query.filter(Post.video_post_publish_delay_seconds < (7 * 24 * 3600))
    if filter_data.get('filter_exclude_nsfw', 'false') == 'true':
        new_query = new_query.filter(not_(Post.is_nsfw))

    return new_query


def apply_sort_to_query(original_query, filter_data):
    new_query = original_query
    sort_order = Post.pending_payout_value.desc()
    if filter_data.get('filter_sort_selection', 'all') == 'date':
        sort_order = Post.created.desc()
    elif filter_data.get('filter_sort_selection', 'all') == 'payout':
        sort_order = Post.pending_payout_value.desc()
    elif filter_data.get('filter_sort_selection', 'all') == 'trending':
        sort_order = Post.trending_score.desc()
    elif filter_data.get('filter_sort_selection', 'all') == 'hot':
        sort_order = Post.hot_score.desc()
    return new_query.order_by(sort_order)


class DBConnection(object):
    """
    This creates a DBConnection object that can be used in a with: block
    This will automatically clean up after itself
    example:
    ```
    with DBConnection() as db:
        users = db.session.query(User).all()
    ```
    """

    def __init__(self, constring=""):
        """
        Create a new instance of the DBConnection Object, for use during a with:
        :param string constring: A specific connection string (default "")
        """
        self.constring = constring
        self.session = None

    def __enter__(self):
        """
        Sets up the entry point of the session
        :return: self
        """
        # Setup the connection string if one's not been provided
        if self.constring == "":
            self.constring = SQLALCHEMY_DATABASE_URI

        # Setup the engine to use
        self.engine = create_engine(self.constring, echo=False)

        # Create a new SessionMaker
        session_maker = sessionmaker(bind=self.engine)

        # create a session with session_maker()
        self.session = session_maker()

        # Return this whole object for use
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Commands to run after with:block has ended
        :param exc_type: NA
        :param exc_val: NA
        :param exc_tb: NA
        :return:
        """
        # Close session
        self.session.close()
        # Dispose of the engine
        self.engine.dispose()
