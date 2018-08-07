import os
import json
import requests
import shlex
import subprocess


class Git2SC():
    '''Class to sync a git documentation repository to Confluence.'''

    def __init__(self, confluence_api_url, auth):
        self.api_url = confluence_api_url
        self.auth = tuple(auth.split(':'))
        self.pages = {}

    def _requests_error(self, requests_object):
        '''Print the confluence error'''

        if requests_object.status_code == 200:
            return
        else:
            response = json.loads(requests_object.text)

            print('Error {}: {}'.format(
                response['statusCode'],
                response['message'],
            ))

    def get_page_info(self, pageid):
        '''Get all the information of a confluence page'''

        url = '{base}/content/{pageid}?expand=ancestors,body.storage,version'\
            .format(base=self.api_url, pageid=pageid)

        r = requests.get(url, auth=self.auth)
        self._requests_error(r)
        return r.json()

    def get_space_homepage(self, spaceid):
        '''Get the homepage of a confluence space'''

        url = '{base}/space/{spaceid}'.format(
            base=self.api_url,
            spaceid=spaceid,
        )
        r = requests.get(url, auth=self.auth)
        self._requests_error(r)
        return r.json()['_expandable']['homepage'].split('/')[4]

    def get_space_articles(self, spaceid):
        '''Get all the pages of a confluence space'''

        url = '{base}/content/?spaceKey={spaceid}'\
            '?expand=ancestors,body.storage,version'.format(
                base=self.api_url,
                spaceid=spaceid,
            )
        r = requests.get(url, auth=self.auth)
        self._requests_error(r)
        self.pages = {}
        for page in r.json()['results']:
            self.pages[page['id']] = page

    def update_page(self, pageid, html, title=None):
        '''Update a confluence page with the content of the html variable'''

        try:
            self.pages[pageid]
        except KeyError:
            self.pages[pageid] = self.get_page_info(pageid)

        version = int(self.pages[pageid]['version']['number']) + 1

        ancestors = self.pages[pageid]['ancestors'][-1]
        del ancestors['_links']
        del ancestors['_expandable']
        del ancestors['extensions']

        if title is not None:
            self.pages[pageid]['title'] = title

        data = {
            'id': str(pageid),
            'type': 'page',
            'title': self.pages[pageid]['title'],
            'version': {'number': version},
            'ancestors': [ancestors],
            'body': {
                'storage':
                {
                    'representation': 'storage',
                    'value': str(html),
                }
            }
        }

        data = json.dumps(data)

        url = '{base}/content/{pageid}'.format(base=self.api_url, pageid=pageid)

        r = requests.put(
            url,
            data=data,
            auth=self.auth,
            headers={'Content-Type': 'application/json'}
        )

        self._requests_error(r)

    def create_page(self, space, title, html, parent_id=None):
        '''Create a confluence page with the content of the html variable'''

        data = {
            'type': 'page',
            'title': title,
            'space': {'key': space},
            'body': {
                'storage': {
                    'value': html,
                    'representation': 'storage'
                },
            },
        }

        if parent_id is not None:
            data['ancestors'] = [{'id': parent_id}]

        data_json = json.dumps(data)

        url = '{base}/content'.format(base=self.api_url)

        r = requests.post(
            url,
            data=data_json,
            auth=self.auth,
            headers={'Content-Type': 'application/json'}
        )

        self._requests_error(r)

    def delete_page(self, pageid):
        '''Delete a confluence page given the pageid'''

        url = '{base}/content/{pageid}'.format(base=self.api_url, pageid=pageid)

        r = requests.delete(
            url,
            auth=self.auth,
        )

        if r.status_code is not 204:
            self._requests_error(r)

    def _safe_load_file(self, file_path):
        '''Takes a file path and loads it in a safe way evading posible
        injections'''

        return os.path.expanduser(shlex.quote(file_path))

    def _process_adoc(self, adoc_file_path):
        '''Takes a path to an adoc file, transform it and return it as
        html'''

        '''Clean the html for shitty confluence
        *
        * autoclose </meta> </link> </img> </br> </col>
        '''

        clean_path = self._safe_load_file(adoc_file_path)

        # Confluence doesn't like the <!DOCTYPE html> line, therefore
        # the split('/n')
        return subprocess.check_output(
            ['asciidoctor', '-b', 'xhtml', clean_path, '-o', '-'],
            shell=False,
        ).decode().replace('<!DOCTYPE html>\n', '')

    def _process_md(self, adoc_file_path):
        '''Takes a path to an md file, transform it and return it as
        html'''

        '''Clean the html for shitty confluence
        *
        * autoclose </meta> </link> </img> </br> </col>
        '''

        clean_path = self._safe_load_file(adoc_file_path)

        # Confluence doesn't like the <!DOCTYPE html> line, therefore
        # the split('/n')
        return subprocess.check_output(
            ['pandoc', clean_path, '-t', 'html', '-o', '-'],
            shell=False,
        ).decode()

    def _process_html(self, html_file_path):
        '''Takes a path to an html file and returns it'''
        clean_path = self._safe_load_file(html_file_path)
        with open(clean_path, 'r') as f:
            return f.read()

    def import_file(self, file_path):
        '''Takes a path to a file and decides which _process.* method to use
        based on the extension'''
        extension = os.path.splitext(file_path)[-1]
        if extension == '.adoc':
            html = self._process_adoc(file_path)
        elif extension == '.html':
            html = self._process_html(file_path)
        elif extension == '.md':
            html = self._process_md(file_path)
        else:
            raise UnknownExtension('Extension {} of file {} not known'.format(
                extension,
                file_path,
            ))
        return html


class UnknownExtension(Exception):
    pass
