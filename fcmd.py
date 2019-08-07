from cmd import Cmd
from ftrack_api import Session
from pprint import pformat
import logging


class FPrompt(Cmd):
    prompt = 'ftrack: '

    @property
    def current(self):
        return self._current_entity

    @property
    def session(self):
        return self._session
    
    @property
    def projects(self):
        projects = self.session.query('select name from Project').all()
        self._listed_entities = projects
        return projects

    @property
    def children(self):
        children = self._current_entity['children']
        self._listed_entities = children
        return children

    def __init__(self, session=None):
        self._session = session
        Cmd.__init__(self)
        self._current_entity = None
        self._listed_entities = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def do_ls(self, line):
        if not self.current:
            projects = self.projects
            project_names = [p['name'] for p in projects]
            for project_name in project_names:
                print project_name
        else:
            entities = self.children
            entity_names = [e['name'] for e in entities]
            for entity_name in entity_names:
                print entity_name

    def complete_cd(self, text, line, start_index, end_index):

        if not self.current:
            projects = self.projects
            project_names = [project['name'] for project in projects]
            if not text:
                return map(str, project_names[:])
                
            else:
                return map(str, [
                    project_name for project_name in project_names
                    if project_name.startswith(text)
                ])

        else:
            entities = self.children
            entity_names = [entity['name'] for entity in entities]
            if not text:
                return entity_names[:]
                
            else:
                return [
                    entity_name for entity_name in entity_names 
                    if entity_name.startswith(text)
                ]
                
    def do_quit(self, args):
        """Quits the program."""
        print "Quitting."
        raise SystemExit

    def do_cd(self, line):
        current = [
            entity for entity in self._listed_entities
            if entity['name'] == line
        ][0]
        self._current_entity = current
  
    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    session = Session()

    prompt = FPrompt(session=session)
    prompt.cmdloop('welcome to ftrack shell...')