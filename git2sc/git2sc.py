import json
import requests


class Git2SC():

    def __init__(self, confluence_api_url, auth):
        self.api_url = confluence_api_url
        self.auth = auth

    def get_page_info(self, pageid):
        '''Get all the information of a confluence page'''

        url = '{base}/content/{pageid}?expand=ancestors,body.storage'.format(
            base=self.api_url,
            pageid=pageid,
        )
        r = requests.get(url, auth=self.auth)
        r.raise_for_status()
        return r.json()

    def get_space_homepage(self, spaceid):
        '''Get the homepage of a confluence space'''

        url = '{base}/space/{spaceid}'.format(
            base=self.api_url,
            spaceid=spaceid,
        )
        req = requests.get(url, auth=self.auth)
        req.raise_for_status()
        return req.json()['_expandable']['homepage'].split('/')[4]

    def get_space_articles(self, spaceid):
        '''Get all the pages of a confluence space'''

        url = '{base}/content/?spaceKey={spaceid}'.format(
                base=self.api_url,
                spaceid=spaceid,
            ) + '?expand=ancestors,body.storage'
        r = requests.get(url, auth=self.auth)
        r.raise_for_status()
        self.pages = {}
        for page in r.json()['results']:
            self.pages[page['id']] = page

    def update_page(self, pageid, html, title=None):

        try:
            self.pages[pageid]
        except KeyError:
            self.pages[pageid] = self.get_page_info(pageid)

        ver = int(self.pages[pageid]['version']['number']) + 1

        anc = self.pages[pageid]['ancestors'][-1]
        del anc['_links']
        del anc['_expandable']
        del anc['extensions']

        if title is not None:
            self.pages[pageid]['title'] = title

        data = {
            'id': str(pageid),
            'type': 'page',
            'title': self.pages[pageid]['title'],
            'version': {'number': ver},
            'ancestors': [anc],
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

        r.raise_for_status()

        print("Wrote '%s' version %d" % (self.pages[pageid]['title'], ver))
