#
# License: See LICENSE file
# GitHub: https://github.com/Baekalfen/PyBoy
#

from .autopause import AutoPause
from .base_plugin import PyBoyPlugin
from .debug import Debug
from .disable_input import DisableInput
from .record_replay import RecordReplay
from .rewind import Rewind
from .screenrecorder import ScreenRecorder
from .window_dummy import DummyWindow
from .window_headless import HeadlessWindow
from .window_opengl import OpenGLWindow
from .window_sdl2 import SDLWindow

windows = [SDLWindow, OpenGLWindow, HeadlessWindow, DummyWindow]
plugins = [DisableInput, AutoPause, RecordReplay, Rewind, ScreenRecorder, Debug]


def get_parser_arguments():
    for p in plugins:
        yield p.argv


class PluginManager(PyBoyPlugin):
    def __init__(self, pyboy, argv):
        super().__init__(pyboy, argv)

        self.windows = []
        self.plugins = []

        for plugin in plugins:
            p = plugin(pyboy, argv)
            if p.enabled():
                self.plugins.append(p)
        for window in windows:
            w = window(pyboy, argv)
            if w.enabled():
                self.windows.append(w)

    def handle_events(self, events):
        for w in self.windows:
            events = w.handle_events(events)
        for p in self.plugins:
            events = p.handle_events(events)
        return events

    def post_tick(self):
        for p in self.plugins:
            p.post_tick()
        if not self.pyboy.paused:
            # This might change, if we have a HUD
            self._post_tick_windows()

    def _post_tick_windows(self):
        for w in self.windows:
            w.post_tick()
            w.set_title(self.pyboy.window_title)

    def frame_limiter(self, speed):
        if speed <= 0:
            return
        for w in self.windows:
            if w.frame_limiter(speed):
                break

    def window_title(self):
        title = ""
        for w in self.windows:
            title += w.window_title()
        for p in self.plugins:
            title += p.window_title()
        return title

    def stop(self):
        for w in self.windows:
            w.stop()
        for p in self.plugins:
            p.stop()