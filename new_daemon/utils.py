import sys
import os
class Util(object):
 
  def find_error_script(self):
    for directory in sys.path:
        full_path = os.path.join(directory, "git-error")
        if (os.path.exists(full_path) and 
            os.access(full_path, (os.F_OK | os.X_OK))):
            return full_path
    raise Exception('Could not find git-error executable!')

  def find_git_shell(self):
    # Find git-shell path.
    # Adapted from http://bugs.python.org/file15381/shutil_which.patch
    path = os.environ.get("PATH", os.defpath)
    for dir in path.split(os.pathsep):
        full_path = os.path.join(dir, 'git-shell')
        if (os.path.exists(full_path) and 
                os.access(full_path, (os.F_OK | os.X_OK))):
            return full_path
    raise Exception('Could not find git executable!')
    
  def getprojectname(self, uri):
        '''Extract the project name alone from a path like /project/views.git'''

        parts = uri.split('/')
        project = parts[-1]
        if len(project) > 4 and project[-4:] == '.git':
            return project[:-4]
        else:
            return project