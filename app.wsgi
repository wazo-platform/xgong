import os
import sys
import xgong
import bottle

xgong.server.setup()
xgong.server.scheduler.start()
application = bottle.default_app()
