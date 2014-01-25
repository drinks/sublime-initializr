import sublime, sublime_plugin
import urllib
import glob
import json
import os
import sys
import shutil
import errno

from io import BytesIO
from zipfile import ZipFile


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


class InitializrProject(sublime_plugin.WindowCommand):
    zf = None
    settings = None

    def run(self):
        self.settings = sublime.load_settings('initializr.sublime-settings')
        self.window.show_input_panel('Where to save your new project?',
                                     '~/newproject', self.create, None, None)

    def create(self, path):
        if path.startswith('~/'):
            path = os.path.expanduser(path)
        path = os.path.realpath(path)
        if os.path.exists(path):
            self.window.show_input_panel('That path exists! Where to save your new project?',
                                         '~/newproject', self.create, None, None)
        self.download(None)
        mkdir_p(path)
        self.zf.extractall(path)
        for fn in glob.glob('%s/initializr/*' % path):
            shutil.move(fn, '%s/' % path)
        os.rmdir('%s/initializr' % path)

        self.finish(path)

    def download(self, url):
        if not url:
            url = self.settings.get('zip_url')
        try:
            self.zf = ZipFile(BytesIO(urllib.request.urlopen(url).read()))
        # For ST2 Compat
        except AttributeError:
            self.zf = ZipFile(BytesIO(urllib.urlopen(url).read()))

    def finish(self, path):
        project_data = {
            'folders': [{
                'follow_symlinks': True,
                'path': path,
            }]
        }
        try:
            sublime.run_command('new_window')
            sublime.active_window().set_project_data(project_data)
        except:
            name = os.path.split(path)[1]
            proj = '%s/%s.sublime-project' % (path, name)
            json.dump(project_data, open(proj, 'w+'))
            sublime.active_window().run_command('close')
            sublime.run_command('prompt_open_project')
