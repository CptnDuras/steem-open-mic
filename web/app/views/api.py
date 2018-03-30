import json
import math
import traceback

import pandas as pd
from flask import jsonify, Blueprint, request, abort
from sqlalchemy import and_
from steem import steem
from datetime import date, datetime
from config import DEBUGGING_KEY
from models import Post, LastBlock
from utilities import apply_filter_to_query, create_video_summary_fields, apply_sort_to_query, get_age_string, \
    get_payout_string, markdown_to_safe_html, get_sparkline_data_from_content, log, DBConnection

api_blueprint = Blueprint("api", __name__)


def get_current_week():
    d0 = date(2016, 9, 25)
    d1 = datetime.now().date()
    delta = d1 - d0
    return math.floor(delta.days/7)


@api_blueprint.route('/api/videos/<type>/<limit>', methods=['GET'])
@api_blueprint.route('/api/videos/<type>', methods=['GET'])
def videos(type, limit=30):
    order_types = {
        "hot": Post.total_payout_value.desc(),
        "new": Post.created.desc(),
        "trending": Post.trending_score.desc()
    }

    if type not in order_types.keys():
        return abort(500)

    limit = int(limit * 1.2)
    order = order_types[type]
    filter_data = {}
    current_week = get_current_week()

    try:
        with DBConnection() as db:
            query = db.session.query(Post)

            query = query.filter(
                # only query the current week
                Post.title.like('%{}%'.format(current_week))
            ).order_by(
                # Order by the correct type
                order
            ).limit(
                # limit appropriately
                limit
            )

            data_frame = pd.read_sql(query.statement, db.session.bind)
            summary = create_video_summary_fields(data_frame, filter_data)
            output = json.loads(summary.head(limit).to_json(orient='records'))

        return jsonify(output)
    except Exception as ex:
        return jsonify(str(ex))



@api_blueprint.route('/api/search/<search_terms>/<limit>', methods=['GET', 'POST'])
@api_blueprint.route('/api/search/<search_terms>', methods=['GET', 'POST'])
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
    except Exception as ex:
        log(f"{ex}\n{traceback.format_exc()}")
        return jsonify([])


@api_blueprint.route('/api/video/@<author>/<permlink>')
def video(author=None, permlink=None):
    from web.app import db

    post = db.session.query(
        Post
    ).filter(
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

        replies = steem.get_content_replies(author, permlink)
        for reply in replies:
            comment = {
                'author': reply['author'],
                'permlink': reply['permlink'],
                'age_string': get_age_string(datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S')),
                'created': datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S'),
                'payout_string': get_payout_string(reply['pending_payout_value'], reply['total_payout_value']),
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


@api_blueprint.route('/api/replies/@<author>/<permlink>')
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


@api_blueprint.route('/api/votes/@<author>/<permlink>')
def votes(author=None, permlink=None):
    return jsonify([])


########################################################################

# DEBUGGING AND EXPERIMENTAL PAGES (NOT USED IN VUE APP) ###############

@api_blueprint.route('/api/vtp/@<author>/<permlink>')
def vote_time_profile(author, permlink):
    from web.app import steem
    content = steem.get_content(author, permlink)
    return get_sparkline_data_from_content(content)


@api_blueprint.route(f'/api/{DEBUGGING_KEY}/raw/@<author>/<permlink>')
def raw(author, permlink):
    from web.app import steem

    content = steem.get_content(author, permlink)
    return content


# shows current replies
@api_blueprint.route(f'/api/{DEBUGGING_KEY}/raw-replies/@<author>/<permlink>')
def raw_replies(author, permlink):
    from web.app import steem

    replies = steem.get_content_replies(author, permlink)
    return str(replies)


@api_blueprint.route(f'/api/{DEBUGGING_KEY}/status/data')
def status_data():
    from web.app import db, steem
    # get the last block from the DB
    try:
        last_block = db.session.query(LastBlock).first().number
    except:
        last_block = 0

    # get the last block from steem
    head_block = steem.head_block_number
    # calculate the delay between the last block on the chain, and the DB
    db_lag = (head_block - last_block) * 3
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

    data = {
        "head_block": head_block,
        "last_block": last_block,
        "db_lag": db_lag,
        "db_posts": db_posts,
        "pending_steem_update": pending_steem,
        "pending_video_update": pending_video,
    }

    # html = f"""
    #     Steem Blockchain Head Block: {head_block} <br>
    #     Database Head Block: {last_block} <br>
    #     Approximate Database Head Delay Seconds: {db_lag} <br>
    #     Posts in Database: {db_posts} <br>
    #     Posts Pending Steem Info Update: {pending_steem} <br>
    #     Posts Pending Video Info Update: {pending_video} <br>
    # """

    return jsonify(data)

