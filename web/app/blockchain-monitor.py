import json
import time
from datetime import datetime
from threading import Thread
from . import app, db
from .models import Post
from .utilities import log, get_valid_video
from sqlalchemy import and_
from steem import Steem
from steem.blockchain import Blockchain

steem = Steem(nodes=app.config['STEEM_NODES'])


def get_block_num(block):
    if not block:
        return -1
    if type(block) == bytes:
        block = block.decode('utf-8')
    if type(block) == str:
        block = json.loads(block)
    return int(block['previous'][:8], base=16) + 1


# called whether adding from files or from the stream
def add_block_content_to_db(block):
    block_number = int(block['previous'][:8], base=16) + 1

    # add qualifying posts, and for edited posts and comments, schedule updates
    try:
        for transaction in block['transactions']:
            for o in transaction['operations']:
                # check for votes for existing video posts, and if so schedule Steem RPC update
                if o[0] == 'vote':
                    try:
                        vote = o[1]
                        post = db.session.query(Post) \
                            .filter(and_(Post.author == vote['author'],
                                         Post.permlink == vote['permlink'])).first()
                        if post:
                            post.pending_steem_info_update = True
                            post.steem_info_update_requested = datetime.now()
                            db.session.commit()

                    except Exception as e:
                        log('Monitor error when evaluating vote...')
                        log(str(e))

                # check for existing post (or add skeleton record if not present) and schedule updates
                if o[0] == 'comment':
                    try:
                        comment = o[1]
                        if comment['parent_author'] == '':  # if top-level post
                            post = db.session.query(Post) \
                                .filter(and_(Post.author == comment['author'],
                                             Post.permlink == comment['permlink'])).first()
                            if post:
                                post.pending_steem_info_update = True
                                post.steem_info_update_requested = datetime.now()
                                post.pending_video_info_update = True
                                post.video_info_update_requested = datetime.now()
                                db.session.commit()
                            else:
                                video_type, video_id, category = get_valid_video(comment)
                                if video_type and video_id and category:
                                    post_skeleton = Post(author=comment['author'], permlink=comment['permlink'],
                                                         category=category, video_type=video_type, video_id=video_id,
                                                         block_number=block_number)
                                    db.session.add(post_skeleton)
                                    db.session.commit()

                    except Exception as e:
                        log('Monitor error when evaluating comment...')
                        log(str(e))

    except Exception as e:
        log('BIG ERROR:' + str(e))
        time.sleep(30)


# todo - check for JSON block files to prepopulate DB
def populate_db_from_raw_blocks_json_files(path, start_date):
    pass


class StreamingBlockSyncThread(Thread):
    def __init__(self, db, app, start_block):
        Thread.__init__(self)
        self.app = app
        self.db = db
        self.start_block = start_block

    # collect blocks from start_block or last collected block by streaming from Steem Node
    def run(self):
        while True:
            try:
                b = Blockchain(Steem(nodes=app.config['STEEM_NODES']))
                log('Using Steem API node(s): ' + str(app.config['STEEM_NODES']))
                log('Blockchain head is ' + str(steem.head_block_number))

                # start from max block present in table
                post = db.session.query(Post).order_by(Post.id.desc()).first()
                if post:
                    self.start_block = post.block_number
                    log('Starting streaming (in catch up) from block: ' + str(self.start_block))
                else:
                    self.start_block = self.start_block
                    log('Starting streaming from (specified) block: ' + str(self.start_block))

                for blockcount, block in enumerate(b.stream_from(start_block=self.start_block, full_blocks=True)):
                    block_number = self.start_block + blockcount
                    if (self.start_block + blockcount) % 20 == 0:
                        log('Read Block:' + str(block_number))
                    try:
                        add_block_content_to_db(block)
                    except Exception as e:
                        log('ERROR: Problem adding block to database.')
                        log(str(e))
                        time.sleep(10)
                        break
            except Exception as e:
                log('ERROR: Problem collecting raw blocks from ' + str(app.config['STEEM_NODES']))
                log(str(e))
                time.sleep(10)


time.sleep(5)
log('Started Blockchain Monitor')
if app.config['RECREATE_DATABASE']:
    log('Dropping/Recreating Database...')
    try:
        db.drop_all()
        db.create_all()
        log('Successfully dropped/recreated. Using new database...')
        time.sleep(1)
    except Exception as e:
        log('Error Dropping/Recreating Database: ' + str(e))
else:
    log('Using existing database...')

# add data from raw JSON block files
# log('Populating DB from Files...')
# populate_db_from_raw_blocks_json_files('/home/app/raw_blocks/', datetime(2017, 6, 1))

hours_to_collect = 4
min_start_block_number = steem.head_block_number - int((3600 / 3 * hours_to_collect))

# start thread for collecting raw blocks info
log('Populating DB from Steem Stream...')
thread_1 = StreamingBlockSyncThread(db, app, min_start_block_number)
thread_1.start()
