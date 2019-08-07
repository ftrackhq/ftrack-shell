from cmd import Cmd
from ftrack_api import Session
from pprint import pformat


class FPrompt(Cmd):
    prompt = 'ftrack: '

    @property
    def current(self):
        return self._current_entity

    @property
    def session(self):
        return self._session

    def __init__(self, *args, **kwargs):
        self._session = kwargs.pop('session')
        Cmd.__init__(self, *args, **kwargs)
        self._current_entity = None
        self._listed_entities = {}
    
    def do_ls(self, *args):
        if not self.current:
            projects = self.session.query('select name from Project').all()
            self._listed_entities = projects
            project_names = [p['name'] for p in projects]
            for project_name in project_names:
                print project_name
        else:
            entities = self._current_entity['children']
            self._listed_entities = entities
            entity_names = [e['name'] for e in entities]
            for entity_name in entity_names:
                print entity_name

    def do_quit(self, args):
        """Quits the program."""
        print "Quitting."
        raise SystemExit

    def do_cd(self, *args):
        current = [
            entity for entity in self._listed_entities
            if entity['name'] == args[0]
        ][0]
        self._current_entity = current


if __name__ == '__main__':
    session = Session()

    prompt = FPrompt(session=session)
    prompt.cmdloop('welcome to ftrack shell...')