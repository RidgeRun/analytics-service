#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""Server entry point
"""

import argparse
from queue import Queue
from threading import Thread

from analytics.controllers.configcontroller import ConfigurationController
from analytics.eventhandler import EventHandler
from analytics.logger import Logger
from analytics.server import Server


def parse_args():
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5040,
                        help="Port for server")
    parser.add_argument("--host", type=str, default='127.0.0.1',
                        help="Server ip address")
    parser.add_argument("--config-file", type=str, default=None,
                        help="Configuration JSON file")

    args = parser.parse_args()

    return args


def main():
    """
    Main application
    """
    Logger.init()
    logger = Logger.get_logger()

    args = parse_args()

    config_queue = Queue()
    event_handler = EventHandler(config_queue, args.config_file)
    configuration = event_handler.configuration

    controllers = []
    controllers.append(ConfigurationController(
        config_queue, configuration=configuration))

    logger.info("Launch flask server")
    server = Server(controllers, host=args.host, port=args.port)
    server_thread = Thread(target=server.start, daemon=True)
    server_thread.start()

    logger.info("Listen to detection events")

    event_handler.loop_events()


if __name__ == "__main__":
    main()
