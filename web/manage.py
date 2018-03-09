#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server

from web.app import app
from models import db

manager = Manager(app)
migrate = Migrate(app, db)

server = Server(host='0.0.0.0', port=5000, use_debugger=True, use_reloader=True)

manager.add_command('db', MigrateCommand)
manager.add_command("run", server)

if __name__ == '__main__':
    manager.run()
