#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""Controller for configuration requests
"""

from flask import request
from flask_cors import cross_origin
from rrmsutils.models.analytics.configuration import Configuration
from rrmsutils.models.apiresponse import ApiResponse

from analytics.controllers.controller import Controller
from analytics.logger import Logger

logger = Logger.get_logger()


class ConfigurationController(Controller):
    """
    Controller for configuration requests
    """

    def __init__(self, queue, configuration=None):
        self._configuration = configuration
        self._queue = queue

    def add_rules(self, app):
        """
        Add configuration rule at /configuration uri
        """
        app.add_url_rule('/configuration', 'configuration',
                         self.configuration, methods=['PUT', 'GET'])

    @cross_origin()
    def configuration(self):
        """Callback for configuration request
        """
        if request.method == 'PUT':
            return self.put_configuration()
        if request.method == 'GET':
            return self.get_configuration()

        data = ApiResponse(
            code=1, message=f'Method {request.method} not supported').model_dump_json()
        return self.response(data, 400)

    def get_configuration(self):
        """Get the current analytics configuration

        Returns:
            str: json string with the current configuration
        """
        configuration = self._configuration
        data = configuration.model_dump_json()
        return self.response(data, 200)

    def put_configuration(self):
        """Set the current configuration according to the json included in request content

        Returns:
            str: json string with the command status
        """
        data = request.json
        try:
            configuration = Configuration.model_validate(data)
        except Exception as e:
            response = ApiResponse(code=1, message=repr(e))
            data = response.model_dump_json()
            return self.response(data, 400)

        self._configuration = configuration
        self._queue.put(configuration)

        logger.info(f'configuration request: {configuration}')
        data = ApiResponse().model_dump_json()
        return self.response(data, 200)
