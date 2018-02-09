# Steem Open Mic system
## Project
So far this is based on mutli-tube, the excellent platform built by andybets https://github.com/andybets/steem-video-aggregator

## Vision
The plan is to be able to list all of the videos from openmic, as well as provide an interface for users to upload their videos as well.

A more detailed technical goal list:
* List all videos on steemit with the tag openmic
* Provide upload of videos/linking to videos with the default tag of openmic
* Group openmic tags based on the current week (i.e. Open Mic week 71 )
* Ability to group by most viewed, highest grossing, newest, most active (most comments/etc.)
* Look good
* deploy on 

## How to Run (for development)

Prerequisites:
* Python3.6
* PostgreSQL database

1. Create/activate a python3 virtual environment
2. Run pip install -r requirements.txt
3.

## Database Schema Migrations
Execute from within running web container...

- % flask db init - Adds a database migrations folder to your application.
- % flask db migrate - Makes a migration script.
- % flask db upgrade - Applies outstanding migrations to the database.

See https://flask-migrate.readthedocs.io for more info.
