import sys

import server
import utils
import validation

utils.populate_plugins()

server.app.config.from_json(sys.argv[1])
server.validate_config()
server.setup_runners()

server.socketio.run(server.app, host="0.0.0.0", port=5000, debug=True)
server.teardown_runners()
