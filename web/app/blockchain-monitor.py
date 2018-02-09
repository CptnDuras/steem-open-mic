import json
import time
import traceback
from datetime import datetime
from threading import Thread
from webapp import app, db
from models import Post
from utilities import log, get_valid_video, DBConnection
from sqlalchemy import and_
from steem import Steem
from steem.blockchain import Blockchain

from web.app.models import LastBlock

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
                operation_type = o[0]
                item = o[1]

                if "author" not in item:
                    return

                author = item['author']
                permlink = item['permlink']

                # check for votes for existing video posts, and if so schedule Steem RPC update
                # if operation_type == 'vote':
                #     try:
                #         with DBConnection() as db:
                #             post = db.session.query(
                #                 Post
                #             ).filter(
                #                 and_(
                #                     Post.author == author,
                #                     Post.permlink == permlink
                #                 )
                #             ).first()
                #
                #             if post:
                #                 post.pending_steem_info_update = True
                #                 post.steem_info_update_requested = datetime.now()
                #                 db.session.commit()
                #
                #     except Exception as ex:
                #         log('Monitor error when evaluating vote...')
                #         log(str(ex))

                # check for existing post (or add skeleton record if not present) and schedule updates

                if operation_type == 'comment':
                    try:
                        try:
                            metadata = json.loads(item["json_metadata"])
                        except Exception as ex:
                            return

                        if "tags" not in metadata or "openmic" not in metadata["tags"] or item['parent_author'] != '':
                            return

                        log(f"Found openmic @ {block_number}")

                        with DBConnection() as db:
                            post = db.session.query(
                                Post
                            ).filter(
                                and_(
                                    Post.author == author,
                                    Post.permlink == permlink
                                )
                            ).first()

                            if not post:
                                post.pending_steem_info_update = True
                                post.steem_info_update_requested = datetime.now()
                                post.pending_video_info_update = True
                                post.video_info_update_requested = datetime.now()
                                db.session.commit()
                                return

                            video_type, video_id, category = get_valid_video(item)
                            if video_type and video_id and category:
                                post_skeleton = Post(
                                    author=author,
                                    permlink=permlink,
                                    category=category,
                                    video_type=video_type,
                                    video_id=video_id,
                                    block_number=block_number
                                )
                                db.session.add(post_skeleton)
                                db.session.commit()

                    except Exception as ex:
                        log('Monitor error when evaluating comment...')
                        log(f"{ex}\n{traceback.format_exc()}")

    except Exception as ex:
        log(f'BIG ERROR:{ex}\n{traceback.format_exc()}')


# todo - check for JSON block files to prepopulate DB
def populate_db_from_raw_blocks_json_files(path, start_date):
    pass


class StreamingBlockSyncThread(Thread):
    def __init__(self, app, start_block):
        Thread.__init__(self)
        self.app = app

        with DBConnection() as db:
            last_block = db.session.query(LastBlock).first()

        if last_block:
            self.start_block = last_block.number
        else:
            self.start_block = start_block

    # collect blocks from start_block or last collected block by streaming from Steem Node
    def run(self):
        while True:
            try:
                nodes = app.config['STEEM_NODES']

                b = Blockchain(Steem(nodes=nodes))

                log(f'Using Steem API node(s): {nodes} ')
                log(f'Blockchain head is {steem.head_block_number}')
                log(f'Starting streaming from (specified) block: {self.start_block}')

                for blockcount, block in enumerate(b.stream_from(start_block=self.start_block, full_blocks=True)):
                    block_number = self.start_block + blockcount

                    if (self.start_block + blockcount) % 10 == 0:
                        # save our progress to the DB
                        with DBConnection() as db:
                            last_block = db.session.query(LastBlock).first()
                            if last_block:
                                last_block.number = block_number
                            else:
                                last_block = LastBlock(block_number)
                            db.session.add(last_block)
                            db.session.commit()

                        # display the last saved block
                        log('Read Block:' + str(block_number))

                    try:
                        add_block_content_to_db(block)
                        # log('Read Block:' + str(block_number))
                    except Exception as ex:
                        log('ERROR: Problem adding block to database.')
                        log(f"{ex}\n{traceback.format_exc()}")
                        break
            except Exception as ex:
                log(f"ERROR: Problem collecting raw blocks from {app.config['STEEM_NODES']}")
                log(f"{ex}\n{traceback.format_exc()}")


log('Started Blockchain Monitor')
if app.config['RECREATE_DATABASE']:
    log('Dropping/Recreating Database...')
    try:
        db.drop_all()
        db.create_all()
        log('Successfully dropped/recreated. Using new database...')
    except Exception as ex:
        log(f"Error Dropping/Recreating Database:{ex}\n{traceback.format_exc()}")
else:
    log('Using existing database...')

# add data from raw JSON block files
# log('Populating DB from Files...')
# populate_db_from_raw_blocks_json_files('/home/app/raw_blocks/', datetime(2017, 6, 1))

hours_to_collect = 4
min_start_block_number = steem.head_block_number - int((3600 / 3 * hours_to_collect))

# start thread for collecting raw blocks info
log('Populating DB from Steem Stream...')
thread_1 = StreamingBlockSyncThread(app, min_start_block_number)
thread_1.start()
