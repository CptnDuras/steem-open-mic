# PUBLIC PAGES ########################################################
import json

import pandas as pd
from flask import request, Blueprint, jsonify
from datetime import datetime

from sqlalchemy import and_, text

from web.app.utilities import apply_filter_to_query, create_video_summary_fields, Post, apply_sort_to_query
from web.app.utilities import get_age_string, markdown_to_safe_html, get_payout_string, get_sparkline_data_from_content
from web.app.config import DEBUGGING_KEY


public_blueprint = Blueprint("public", __name__)


@public_blueprint.route('/f/api/trending-videos/<limit>', methods=['GET', 'POST'])
@public_blueprint.route('/f/api/trending-videos', methods=['GET', 'POST'])
def trending_videos(limit="30"):
    from web.app import db

    limit = int(limit)
    filter_data = {}
    query = db.session.query(Post)
    if request.method == 'POST':
        data = request.data
        filter_data = json.loads(data)
        query = apply_filter_to_query(query, filter_data)
    # get more records than needed as post query filters may remove some
    query = query.order_by(Post.trending_score.desc()).limit(int(limit * 1.2))
    df = pd.read_sql(query.statement, db.session.bind)
    df = create_video_summary_fields(df, filter_data)
    df = df.head(limit)
    return df.to_json(orient='records')


@public_blueprint.route('/f/api/hot-videos/<limit>', methods=['GET', 'POST'])
@public_blueprint.route('/f/api/hot-videos', methods=['GET', 'POST'])
def hot_videos(limit="30"):
    from web.app import db
    limit = int(limit)
    filter_data = {}
    query = db.session.query(Post)
    if request.method == 'POST':
        data = request.data
        filter_data = json.loads(data)
        query = apply_filter_to_query(query, filter_data)
    # get more records than needed as post query filters may remove some
    query = query.order_by(Post.hot_score.desc()).limit(int(limit * 1.2))
    df = pd.read_sql(query.statement, db.session.bind)
    df = create_video_summary_fields(df, filter_data)
    df = df.head(limit)
    return df.to_json(orient='records')


@public_blueprint.route('/f/api/new-videos/<limit>', methods=['GET', 'POST'])
@public_blueprint.route('/f/api/new-videos', methods=['GET', 'POST'])
def new_videos(limit="30"):
    from web.app import db

    limit = int(limit)
    filter_data = {}
    try:
        query = db.session.query(Post)
        if request.method == 'POST':
            data = request.data
            filter_data = json.loads(data)
            query = apply_filter_to_query(query, filter_data)
        # get more records than needed as post query filters may remove some
        query = query.order_by(Post.created.desc()).limit(int(limit * 1.2))
        df = pd.read_sql(query.statement, db.session.bind)
        df = create_video_summary_fields(df, filter_data)
        df = df.head(limit)
        return df.to_json(orient='records')
    except Exception as e:
        return str(e)


@public_blueprint.route('/f/api/search/<search_terms>/<limit>', methods=['GET', 'POST'])
@public_blueprint.route('/f/api/search/<search_terms>', methods=['GET', 'POST'])
def search(search_terms, limit='50'):
    from web.app import db

    limit = int(limit)
    if request.method == 'GET':
        filter_data = json.loads(request.args.get("json"))
    elif request.method == 'POST':
        data = request.data
        filter_data = json.loads(data)
    try:
        author_filter = (Post.author == search_terms)
        modified_search_terms = "'" + search_terms + "'"
        title_filter = Post.title_ts_vector.match(modified_search_terms, postgresql_regconfig='english')
        tags_filter = Post.tags_ts_vector.match(modified_search_terms, postgresql_regconfig='english')
        query = db.session.query(Post).filter(author_filter | title_filter | tags_filter)
        query = apply_filter_to_query(query, filter_data)
        query = apply_sort_to_query(query, filter_data)
        query = query.limit(int(limit * 1.2))  # get more records than needed as post query filters may remove some
        df = pd.read_sql(query.statement, db.session.bind)
        df = create_video_summary_fields(df, filter_data)
        df = df.head(limit)
        return df.to_json(orient='records')
    except Exception as e:
        return jsonify([])


@public_blueprint.route('/f/api/video/@<author>/<permlink>')
def video(author=None, permlink=None):
    from web.app import db

    post = db.session.query(
        Post).filter(
        and_(Post.author == author, Post.permlink == permlink)
    ).order_by(
        Post.video_info_update_requested
    ).first()

    if post:
        post_dict = {
            'title': post.title,
            'author': post.author,
            'permlink': post.permlink,
            'age_string': get_age_string(post.created),
            'created': post.created,
            'tags': post.tags.split(' '),
            'description': markdown_to_safe_html(post.description),
            'payout_string': get_payout_string(post.pending_payout_value + post.total_payout_value),
            'upvotes': 0,
            'downvotes': 0,
            'video_type': post.video_type,
            'video_id': post.video_id,
            'video_source': ''
        }

        comments = []
        if True:
            replies = steem.get_content_replies(author, permlink)
            for reply in replies:
                comment = {
                    'author': reply['author'],
                    'permlink': reply['permlink'],
                    'age_string': get_age_string(datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S')),
                    'created': datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S'),
                    'payout_string': get_payout_string(float(reply['pending_payout_value'].split(' ')[0]) + float(
                        reply['total_payout_value'].split(' ')[0])),
                    'body': markdown_to_safe_html(reply['body']),
                    'reply_count': int(reply['children']),
                    'upvotes': 0,
                    'downvotes': 0
                }
                comments.append(comment)
            post_dict['comments'] = comments

        return jsonify(post_dict)
    else:
        return 'Video Not Found for: ' + str(author) + '/' + str(permlink)


@public_blueprint.route('/f/api/replies/@<author>/<permlink>')
def replies(author=None, permlink=None):
    from web.app import steem

    replies = steem.get_content_replies(author, permlink)
    comments = []
    for reply in replies:
        comment = {
            'author': reply['author'],
            'permlink': reply['permlink'],
            'age_string': get_age_string(datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S')),
            'created': datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S'),
            'payout_string': get_payout_string(
                float(reply['pending_payout_value'].split(' ')[0]) + float(reply['total_payout_value'].split(' ')[0])),
            'body': markdown_to_safe_html(reply['body']),
            'reply_count': int(reply['children']),
            'upvotes': 0,
            'downvotes': 0
        }
        comments.append(comment)
    return jsonify(comments)


# todo - implement for when users click on payout, to show breakdown from db
@public_blueprint.route('/f/api/votes/@<author>/<permlink>')
def votes(author=None, permlink=None):
    return jsonify([])


########################################################################

# DEBUGGING AND EXPERIMENTAL PAGES (NOT USED IN VUE APP) ###############

@public_blueprint.route('/f/api/vtp/@<author>/<permlink>')
def vote_time_profile(author, permlink):
    from web.app import steem
    content = steem.get_content(author, permlink)
    return str(get_sparkline_data_from_content(content))


@public_blueprint.route(f'/f/api/{DEBUGGING_KEY}/raw/@<author>/<permlink>')
def raw(author, permlink):
    from web.app import steem
    content = steem.get_content(author, permlink)
    return str(content)


# shows current replies
@public_blueprint.route(f'/f/api/{DEBUGGING_KEY}/raw-replies/@<author>/<permlink>')
def raw_replies(author, permlink):
    from web.app import steem
    replies = steem.get_content_replies(author, permlink)
    return str(replies)


@public_blueprint.route(f'/f/api/{DEBUGGING_KEY}/status')
def status():
    from web.app import db, steem
    # get the last block from the DB
    try:
        last_block = db.session.query(Post).order_by(Post.id.desc()).first().block_number
    except:
        last_block = 0

    # get the last block from steem
    head_block = steem.head_block_number
    # calculate the delay between the last block on the chain, and the DB
    db_delay = (head_block - last_block) * 3
    # Get the number of posts in the DB
    db_posts = db.session.query(Post.id).count()
    # See how many posts are needing steem update
    pending_steem = db.session.query(Post.id).filter(
        Post.pending_steem_info_update == True
    ).count()
    # see how many posts are needing video update
    pending_video = db.session.query(Post.id).filter(
        Post.pending_video_info_update == True
    ).count()

    html = f"""
        Steem Blockchain Head Block: {head_block} <br>
        Database Head Block: {last_block} <br>
        Approximate Database Head Delay Seconds: {db_delay} <br>
        Posts in Database: {db_posts} <br>
        Posts Pending Steem Info Update: {pending_steem} <br>
        Posts Pending Video Info Update: {pending_video} <br>
    """

    return html


# to explore how better full text search might be done
# todo - establish whether existing indexes are used in the query below (suspect not)
@public_blueprint.route(f'/f/api/{DEBUGGING_KEY}/test-search/<search_terms>', methods=['GET', 'POST'])
def test_search(search_terms):
    from web.app import db

    try:
        sql = text('''
                    SELECT pid, p_title
                    FROM (SELECT posts.id as pid,
                                 posts.title as p_title,
                                 setweight(to_tsvector('english', posts.title), 'A') ||
                                 setweight(to_tsvector('english', posts.tags), 'A') ||
                                 setweight(to_tsvector('simple', posts.author), 'A') as document
                          FROM posts) as p_search
                    WHERE p_search.document @@ to_tsquery('english', 'acoustic <-> guitar')
                    ORDER BY ts_rank(p_search.document, to_tsquery('english', 'acoustic <-> guitar')) DESC;
                   ''')
        df = pd.read_sql(sql, db.session.connection())
        return df.to_html()

    except Exception as e:
        return str(e)

#######################################################################
