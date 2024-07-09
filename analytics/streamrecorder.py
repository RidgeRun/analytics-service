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
Stream recorder
"""
import requests


class StreamRecorder():
    """
    Stream recorder class.

    Provides convenient functions to start VST's recordings
    """

    def __init__(self, vst_uri):
        self._vst_uri = vst_uri

        if not self._vst_uri.endswith("/"):
            self._vst_uri = self._vst_uri + "/"

    def record_event(self, sensor_id):
        """
        Starts event record for sensor

        Args:
           sensor_id (str): The sensor ID from VST

        Raise exception if request failed
        """
        resp = requests.post(f"{self._vst_uri}api/v1/record/{sensor_id}/event")
        if resp.status_code != 200:
            raise RuntimeError(f"Event record failed: {resp}")
