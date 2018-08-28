import os
import json
import shlex
import requests
import pypandoc
import subprocess


class Git2SC():
    '''Class to sync a git documentation repository to Confluence.'''

    def __init__(self, confluence_api_url, auth, space_id):
        self.api_url = confluence_api_url
        self.auth = tuple(auth.split(':'))
        self.space = space_id
        self.pages = {}
        self.get_space_articles()

    def _requests_error(self, requests_object):
        '''Print the confluence error'''

        if requests_object.status_code == 200:
            return
        else:
            response = json.loads(requests_object.text)

            raise Exception('Error {}: {}'.format(
                response['statusCode'],
                response['message']
            ))

    def get_page_info(self, pageid):
        '''Get all the information of a confluence page'''

        url = '{base}/content/{pageid}?expand=ancestors,body.storage,version'\
            .format(base=self.api_url, pageid=pageid)

        r = requests.get(url, auth=self.auth)
        self._requests_error(r)
        return r.json()

    def get_space_homepage(self):
        '''Get the homepage of a confluence space'''

        url = '{base}/space/{spaceid}'.format(
            base=self.api_url,
            spaceid=self.space,
        )
        r = requests.get(url, auth=self.auth)
        self._requests_error(r)
        return r.json()['_expandable']['homepage'].split('/')[4]

    def get_space_articles(self):
        '''Get all the pages of a confluence space'''

        url = '{base}/space/{spaceid}/'\
            'content?expand=body.storage&limit=5000&start=0'.format(
                base=self.api_url,
                spaceid=self.space,
            )
        r = requests.get(url, auth=self.auth)
        self._requests_error(r)
        self.pages = {}
        for page in r.json()['page']['results']:
            self.pages[page['id']] = page

    def _get_article_id(self, title):
        '''Get the id of the article with the specified title'''

        try:
            article_id = [
                pageid
                for pageid, content in self.pages.items()
                if content['title'] == title
            ][0]
        except IndexError:
            article_id = None
        return article_id

    def _title_exist(self, title):
        '''You can't create more than one article with a specified title, test
        if title exists in the existing pages'''
        titles = [content['title'] for page, content in self.pages.items()]
        return title in titles

    def update_page(self, pageid, html, title=None):
        '''Update a confluence page with the content of the html variable'''

        try:
            self.pages[pageid]['version']
        except KeyError:
            self.pages[pageid] = self.get_page_info(pageid)

        version = int(self.pages[pageid]['version']['number']) + 1

        ancestors = self.pages[pageid]['ancestors'][-1:]
        if ancestors != []:
            del ancestors[0]['_links']
            del ancestors[0]['_expandable']
            del ancestors[0]['extensions']

        if title is not None:
            self.pages[pageid]['title'] = title

        data = {
            'id': str(pageid),
            'type': 'page',
            'title': self.pages[pageid]['title'],
            'version': {'number': version},
            'ancestors': ancestors,
            'body': {
                'storage':
                {
                    'representation': 'storage',
                    'value': str(html),
                }
            }
        }

        data_json = json.dumps(data)

        url = '{base}/content/{pageid}'.format(base=self.api_url, pageid=pageid)

        r = requests.put(
            url,
            data=data_json,
            auth=self.auth,
            headers={'Content-Type': 'application/json'}
        )

        self._requests_error(r)

    def create_page(self, title, html, parent_id=None):
        '''Create a confluence page with the content of the html variable'''

        new_title = title
        for counter in range(1, 10):
            if not self._title_exist(new_title):
                break
            new_title = '{}_{}'.format(title, counter)

        data = {
            'type': 'page',
            'title': new_title,
            'space': {'key': self.space},
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

        pageid = json.loads(r.text)['id']
        self.pages[pageid] = self.get_page_info(pageid)
        return pageid

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

    def _process_md(self, md_file_path):
        '''Takes a path to an md file, transform it and return it as
        html'''

        clean_path = self._safe_load_file(md_file_path)

        return pypandoc.convert_file(clean_path, 'html')

    def _process_html(self, html_file_path):
        '''Takes a path to an html file and returns it'''
        clean_path = self._safe_load_file(html_file_path)
        with open(clean_path, 'r') as f:
            return f.read()

    def _process_mainpage(self, directory_path):
        '''Takes a path to a file and updates the confluence homepage'''
        homepage_id = self.get_space_homepage()
        html = self._discover_directory_readme(directory_path)
        self.update_page(homepage_id, html)
        return homepage_id

    def _discover_directory_readme(self, directory_path, parent_id=None):
        '''Takes a directory path, searches for README.adoc or README.md and
        returns it's html'''

        adoc_file = os.path.join(directory_path, 'README.adoc')
        md_file = os.path.join(directory_path, 'README.md')
        if os.path.isfile(adoc_file):
            readme_file = adoc_file
        elif os.path.isfile(md_file):
            readme_file = md_file
        else:
            return "No README here, keep on looking :("

        return self.import_file(readme_file)

    def _create_directory_readme(self, directory_path, parent_id=None):
        '''Takes a directory path, searches for README.adoc or README.md and
        creates a confluence page with that information'''
        return self.create_page(
            os.path.basename(directory_path),
            self._discover_directory_readme(directory_path),
            parent_id,
        )

    def _update_directory_readme(self, directory_path):
        '''Takes a directory path, deduces the article_id and updates it with
        the contents of the README.adoc or README.md'''
        self.update_page(
            self._get_article_id(os.path.basename(directory_path)),
            self._discover_directory_readme(directory_path),
        )

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

    def directory_full_upload(
        self,
        path,
        excluded_items,
        parent_id=None
    ):
        '''Takes a path to a directory and crawls all the subdirectories and
        files and uploads them to confluence.

        The uploaded files are the ones supported by the import_file method.

        Optionally you can set up a parent_id to create the confluence structure
        hanging below a confluence article id
        '''

        is_root_directory = True
        parent_ids = {}
        parent_ids[path] = parent_id
        for root, directories, files in os.walk(path):
            if is_root_directory and parent_id is None:
                self._process_mainpage(root)
            elif is_root_directory and parent_id is not None:
                parent_id = self._create_directory_readme(
                    root,
                    parent_id,
                )
                parent_ids[root] = parent_id
            else:
                directory_parent_id = parent_ids[os.path.dirname(root)]
                parent_id = self._create_directory_readme(
                    root,
                    directory_parent_id,
                )
                parent_ids[root] = parent_id
            is_root_directory = False

            for file in files:
                filename = os.path.splitext(os.path.basename(file))[0]

                try:
                    html = self.import_file(
                        os.path.join(root, file)
                    )
                except UnknownExtension:
                    continue

                if not filename == 'README' and file not in excluded_items:
                    self.create_page(
                        filename,
                        html,
                        parent_id,
                    )

            for directory in directories:
                if directory in excluded_items:
                    directories.remove(directory)

    def directory_update(
        self,
        path,
        excluded_items,
        parent_id=None
    ):
        '''Takes a path to a directory and crawls all the subdirectories and
        files and updates them on confluence.

        The uploaded files are the ones supported by the import_file method.

        Optionally you can set up a parent_id to create the confluence structure
        hanging below a confluence article id.

        Right now it will update or create each article even though it doesn't
        have any changes.
        '''

        is_root_directory = True
        parent_ids = {}
        processed_articles_ids = []
        parent_ids[path] = parent_id
        for root, directories, files in os.walk(path):
            if is_root_directory and parent_id is None:
                article_id = self._process_mainpage(root)
            else:
                article_id = self._get_article_id(os.path.basename(root))
                if is_root_directory:
                    directory_parent_id = parent_id
                else:
                    directory_parent_id = parent_ids[os.path.dirname(root)]
                if article_id is not None:
                    self._update_directory_readme(root)
                else:
                    article_id = self._create_directory_readme(
                        root,
                        directory_parent_id,
                    )
                parent_ids[root] = article_id
            processed_articles_ids.append(article_id)

            for file in files:
                filename = os.path.splitext(os.path.basename(file))[0]

                try:
                    html = self.import_file(
                        os.path.join(root, file)
                    )
                except UnknownExtension:
                    continue

                if not filename == 'README' and file not in excluded_items:
                    article_id = self._get_article_id(filename)

                    if article_id in processed_articles_ids:
                        continue
                    directory_parent_id = parent_ids[root]

                    if article_id is not None:
                        self.update_page(
                            article_id,
                            html,
                        )
                    else:
                        article_id = self.create_page(
                            filename,
                            html,
                            directory_parent_id,
                        )
                    processed_articles_ids.append(article_id)

            for directory in directories:
                if directory in excluded_items:
                    directories.remove(directory)

            is_root_directory = False

        for page_id in self.pages.keys():
            if page_id not in processed_articles_ids:
                self.delete_page(page_id)


class UnknownExtension(Exception):
    pass
