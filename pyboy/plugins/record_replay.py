#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import base64
import hashlib
import io
import json
import zlib

import numpy as np
from pyboy.logger import logger
from pyboy.plugins.base_plugin import PyBoyPlugin


class RecordReplay(PyBoyPlugin):
    def __init__(self, pyboy):
        self.pyboy = pyboy

        if not argv.loadstate:
            logger.warning("To replay input consistently later, it is required to load a state at boot. This will be"
                           "embedded into the .replay file.")

        logger.info("Recording event inputs")
        self.recorded_input = []


    def pre_tick(self):
        # Input recorder
        if self.record_input and len(self.events) != 0:
            self.recorded_input.append((self.frame_count, self.events, base64.b64encode(
                np.ascontiguousarray(self.get_screen_ndarray())).decode('utf8')))


    def handle_events(self, events):
        return events

    def stop(self):
        save_replay(self.pyboy.gamerom_file, argv.loadstate, argv.record_input, self.recorded_input)

def save_replay(rom, loadstate, replay_file, recorded_input):
    with open(rom, 'rb') as f:
        m = hashlib.sha256()
        m.update(f.read())
        b64_romhash = base64.b64encode(m.digest()).decode('utf8')

    if loadstate is None:
        b64_state = None
    else:
        with open(loadstate, 'rb') as f:
            b64_state = base64.b64encode(f.read()).decode('utf8')

    with open(replay_file, 'wb') as f:
        recorded_data = io.StringIO()
        json.dump([recorded_input, b64_romhash, b64_state], recorded_data)
        f.write(zlib.compress(recorded_data.getvalue().encode('ascii')))