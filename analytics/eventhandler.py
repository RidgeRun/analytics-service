#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""
Execute action when event occurs
"""
import json
import time

import redis
from rrmsutils.models.analytics.configuration import Configuration
from rrmsutils.models.ptz.position import Position
from rrmsutils.models.ptz.zoom import Zoom
from rrmsutils.ptz import PTZ

from analytics.logger import Logger
from analytics.streamrecorder import StreamRecorder

logger = Logger.get_logger()


class EventHandler:
    """
    Event handler class
    """

    def __init__(self, config_queue, config_file=None, redis_host="localhost",
                 redis_port=6379, redis_stream="detection"):
        self.configuration = None
        self._config_queue = config_queue
        self._redis_host = redis_host
        self._redis_port = redis_port
        self._redis_stream = redis_stream
        self._actions = {
            "record": {
                "enable": False,
                "function": self._record_action,
                "uri": None
            },
            "move": {
                "enable": False,
                "function": self._ptz_action,
                "uri": None
            }
        }
        self._last_record_time = 0
        self._last_ptz_time = 0

        self._time_to_record = 10
        self._restart_time = 20

        self._reset = False

        if config_file:
            self.configuration = self.get_file_configuration(config_file)
            if self.configuration is not None:
                self._parse_configuration(self.configuration)
            else:
                logger.warning("Couldn't parse configuration file. By default "
                               "the actions are disabled, use the API to update the "
                               "configuration or restart using a configuration file "
                               "with the correct format.")

    def _parse_configuration(self, configuration):

        self._actions['record']['enable'] = configuration.record.enable
        self._actions['move']['enable'] = configuration.move_camera.enable

        logger.info(
            f"Update configuration: record enable={self._actions['record']['enable']}"
            f" move enable={self._actions['move']['enable']}")

        uri = 'http://' + configuration.record.ip + \
            ':' + str(configuration.record.port)
        if uri != self._actions['record']['uri']:
            self._actions['record']['uri'] = uri
            logger.info(f"Update record uri to {uri}")
            self._stream_recorder = StreamRecorder(uri)

        self._time_to_record = configuration.record.time_threshold

        uri = 'http://' + configuration.move_camera.ip + \
            ':' + str(configuration.move_camera.port)
        if uri != self._actions['move']['uri']:
            self._actions['move']['uri'] = uri
            logger.info(f"Update move camera uri to {uri}")
            self._ptz = PTZ(configuration.move_camera.ip,
                            configuration.move_camera.port)

        self._restart_time = configuration.move_camera.time_threshold

    def get_file_configuration(self, config_file):
        """
        Get Configuration from file

        Returns:
            Configuration: an object with the file configuration

        """
        with open(config_file, encoding="utf-8") as json_config:
            try:
                config = json.load(json_config)
                configuration = Configuration.model_validate(config)
            except Exception as e:
                logger.warning(
                    f"Failed to validate file configuration: {repr(e)}")
                configuration = None
        return configuration

    def _record_action(self, metadata):
        """
        Start record for sensor in metadata
        Args:
           metadata(): JSON event schema
        """

        current_time = time.time()
        if self._last_record_time:
            elapsed_time = current_time - self._last_record_time
            if elapsed_time < self._time_to_record:
                logger.debug("Skipping detection record")
                return

        # Get sensor Id from schema
        sensor_id = metadata['sensorId']

        logger.debug(f'starting record for sensor: {sensor_id}')
        try:
            self._stream_recorder.record_event(sensor_id)
        except Exception as e:
            logger.warning(f"Failed to start record {repr(e)}")

        self._last_record_time = current_time

    def _ptz_action(self, metadata):
        """
        Move camera to detected object in metadata
        Args:
           metadata(): JSON event schema
        """
        objects = metadata['objects'][0]
        bbox = objects.split('|')
        bbox_left = float(bbox[0])
        bbox_right = float(bbox[2])
        bbox_top = float(bbox[1])
        bbox_bottom = float(bbox[3].strip('[]'))

        logger.debug(f"bbox left:{bbox_left}, right: {bbox_right},"
                     f"top:{bbox_top}, bottom:{bbox_bottom}, type: {bbox[4]}")
        width = metadata['width']
        height = metadata['height']

        bbox_width = bbox_right - bbox_left
        bbox_height = bbox_bottom - bbox_top

        bbox_center_x = bbox_width/2 + bbox_left
        bbox_center_y = bbox_height/2 + bbox_top

        # Calculate pan and tilt to center the bounding box
        pan = (bbox_center_x - width/2) * 360/width
        tilt = (bbox_center_y - height/2) * 180/height

        # Calculate zoom to fit the bounding box
        if bbox_width > bbox_height:
            ratio = height/bbox_width/2
        else:
            ratio = height/bbox_height/2

        self._set_ptz(pan, tilt, ratio)
        self._last_ptz_time = time.time()
        self._reset = True

    def _set_ptz(self, pan, tilt, zoom):
        """
        Set PTZ position and zoom with the given values

        Args:
           pan (float): The camera pan angle
           tilt (float): The camera tilt angle
           zoom (float): The camera zoom
        """
        position = Position(pan=pan, tilt=tilt)
        zoom = Zoom(zoom=zoom)

        logger.debug(f"move camera: pan={pan}, tilt={tilt}, zoom={zoom}")

        ret = self._ptz.set_position(position)
        if not ret:
            logger.warning("Failed to move camera to bounding box")

        ret = self._ptz.set_zoom(zoom)
        if not ret:
            logger.warning("Failed to zoom camera to bounding box")

    def _restart_position(self):
        """
        Restart ptz position and zoom if restart time has passed without a new
        detection event
        """

        if not self._reset:
            return

        current_time = time.time()
        if self._last_ptz_time:
            elapsed_time = current_time - self._last_ptz_time
            if elapsed_time < self._restart_time:
                return

        self._set_ptz(0, 0, 1)
        self._reset = False

    def loop_events(self):
        """
        Execute enabled actions when receive a redis message
        """
        redis_server = redis.Redis(host=self._redis_host, port=self._redis_port,
                                   decode_responses=True)

        while True:

            if not self._config_queue.empty():
                self._parse_configuration(self._config_queue.get())

            info = redis_server.xread(count=1, block=5000, streams={
                                      self._redis_stream: '$'})
            if not info:
                # Check if ptz need to be restarted when timeout
                if self._actions['move']['enable']:
                    self._restart_position()
                continue

            logger.debug(f'new event: {info}')

            # Get message metadata
            _, data = info[0][1][0]
            metadata = json.loads(data['metadata'])

            for action in self._actions.values():
                if action['enable']:
                    action['function'](metadata)
