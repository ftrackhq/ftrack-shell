from cmd import Cmd
import ftrack_api
import colorama
from colorama import Fore, Back, Style

from pprint import pformat
import logging

colorama.init()

default_prompt = Fore.MAGENTA + 'ftrack: ' + Style.RESET_ALL


class FShell(Cmd):
    prompt = default_prompt
    intro = (Fore.GREEN + 'Welcome to ftrack shell!' + Style.RESET_ALL)

    @property
    def current(self):
        return self._current_entity

    @property
    def session(self):
        return self._session
    
    @property
    def parent(self):
        parent = self.current['parent']
        return parent

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

    def set_prompt(self, text=None):
        if not text:
            self.prompt = default_prompt
        else:
            self.prompt = Fore.MAGENTA + 'ftrack [{}]: '.format(text) + Style.RESET_ALL

    def do_info(self, line):
        if not line:
            for k, v in self._current_entity.items():
                if isinstance(v, ftrack_api.collection.Collection):
                    v = pformat(list(v))
                
                if isinstance(v, ftrack_api.collection.KeyValueMappedCollectionProxy):
                    v = pformat(dict(v))

                print k, ':',  v

        if line and line in self._current_entity:
            v = self._current_entity[line]
            if isinstance(v, ftrack_api.collection.Collection):
                v = pformat(list(v))
            
            if isinstance(v, ftrack_api.collection.KeyValueMappedCollectionProxy):
                v = pformat(dict(v))
                    
            print line, ':', v

    def complete_info(self, text, line, start_index, end_index):
        return [
            key for key in self._current_entity.keys()
            if key.startswith(text)
        ]

    def do_ls(self, line):
        if not self.current:
            projects = self.projects
            project_names = [(p['name'], p.entity_type) for p in projects]
            for project_name, entity_type in project_names:
                print project_name

        else:    
            entities = self.children
            entity_names = [(e['name'], e.entity_type) for e in entities]
            for entity_name, entity_type in entity_names:
                print entity_name

    def complete_cd(self, text, line, start_index, end_index):
        results = []

        if not self.current:
            projects = self.projects
            project_names = [project['name'] for project in projects]
            if not text:
                results = project_names[:]
                
            else:
                results = [
                    project_name for project_name in project_names
                    if project_name.startswith(text)
                ]

        else:
            entities = self.children
            entity_names = [entity['name'] for entity in entities]
            if not text:
                results = entity_names[:]
                
            else:
                results = [
                    entity_name for entity_name in entity_names 
                    if entity_name.startswith(text)
                ]
    
        return results
                
    def do_quit(self, args):
        """Quits the program."""
        print "Quitting."
        raise SystemExit

    def do_cd(self, line):
        current = None
        if line == '..':
            if self.current:
                current = self.parent
        else:
            current = [
                entity for entity in self._listed_entities
                if entity['name'] == line
            ][0]
        
        if current is not None:
            self.set_prompt(
                '{}:{}'.format(current.entity_type, current['name'])
            )
        else:
            self.set_prompt()
    
        self._current_entity = current
  
    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    session = ftrack_api.Session()

    prompt = FShell(session=session)
    prompt.cmdloop()