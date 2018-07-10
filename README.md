# Git2sC

`git2sc` is a program to sync a git documentation repository to Confluence.

# Install

```bash
git clone https://git.paradigmadigital.com/seguridad/git2sc
virtualenv -p python3 git2sc
source git2sc/bin/activate
python3 setup.py install
```

Set up the credentials in the environment variables:

* `GIT2SC_API_URL`: `https://company.atlassian.net/wiki/rest/api`
* `GIT2SC_AUTH`: `username:password`

# Usage

## Update an article

This command will update the confluence article with id `{{ article_id }}` with
the HTML string `{{ content }}`.

```bash
git2sc article {{ article_id }} {{ content }}
```

# Test

To run the tests first install `tox`

```bash
pip3 install tox
```

And then run the tests

```bash
tox
```

# Authors

jamatute@paradigmadigital.com
