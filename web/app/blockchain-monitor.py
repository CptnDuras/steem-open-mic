import json
import traceback
from datetime import datetime
from threading import Thread
from webapp import app, db
from models import Post
from utilities import log, get_valid_video, DBConnection
from sqlalchemy import and_
from steem import Steem
from steem.blockchain import Blockchain

from models import LastBlock

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
def scan_block(block):
    block_number = int(block['previous'][:8], base=16) + 1

    # add qualifying posts, and for edited posts and comments, schedule updates
    for transaction in block['transactions']:
        for o in transaction['operations']:
            try:
                operation_type = o[0]
                # fail right away if it's not a comment
                if operation_type != "comment":
                    continue

                item = o[1]

                # if there's no author, nor metadata, then get right on out of here
                if "author" not in item or item["json_metadata"] == "false":
                    continue

                # check to see if the transaction has the right tag(s)
                if not find_tags(item):
                    continue

                # if we've gotten here, then we have the right item
                log(f"Found openmic @ {block_number}")

                # try to insert a record into the DB
                insert_record(item, block_number)
            except Exception as ex:
                log(f'ERROR:{ex}\n{traceback.format_exc()}')


def find_tags(transaction, tags=None):
    # if no tags are provided, set a default
    if tags is None:
        tags = ["openmic"]

    # load metadata
    metadata = load_metadata(transaction)

    # Check to see if the metadata is ok
    if metadata is None or "tags" not in metadata or transaction['parent_author'] != '':
        return False

    # now loop through the tags on the post to see if they're acceptable
    for tag in metadata["tags"]:
        if tag in tags:
            # if we find a valid tag, return True
            return True

    # if we get here, there's no hope of adding this item
    return False


def load_metadata(transaction):
    """
    Try loading metadata for an item. This is wonky because sometimes data is double encoded
    :param transaction: transaction to load metadata for
    :return: dict of transaction
    """
    try:
        # double load the metadata since that occasionally
        return json.loads(json.loads(transaction["json_metadata"]))
    except Exception as ex1:
        try:
            return json.loads(transaction["json_metadata"])
        except Exception as ex2:
            return None


def insert_record(item, block_number):
    author = item['author']
    permlink = item['permlink']

    with DBConnection() as db:
        post = db.session.query(
            Post
        ).filter(
            and_(
                Post.author == author,
                Post.permlink == permlink
            )
        ).first()

        if post:
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

                    if (self.start_block + blockcount) % 100 == 0:
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
                        scan_block(block)
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
min_start_block_number = steem.head_block_number - int((3600 / 1 * hours_to_collect))

# start thread for collecting raw blocks info
log('Populating DB from Steem Stream...')
thread_1 = StreamingBlockSyncThread(app, min_start_block_number)
thread_1.start()
