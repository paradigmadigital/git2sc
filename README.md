# Git2sC

`git2sc` is a program to sync a git documentation repository to Confluence.

# Install

```bash
git clone https://git.paradigmadigital.com/seguridad/git2sc
cd git2sc
virtualenv -p python3 git2sc
source git2sc/bin/activate
pip3 install -r requirements.txt
python3 setup.py install
```

Set up the credentials in the environment variables:

* `GIT2SC_API_URL`: `https://company.atlassian.net/wiki/rest/api`
* `GIT2SC_AUTH`: `username:password`

# Usage

## Update an article

This command will update the confluence article with id `{{ article_id }}` with
the content of the file in the path `{{ content }}`.

```bash
git2sc article update {{ article_id }} {{ content }}
```

## Create an article

This command will create an confluence article under the `{{ space }}` space,
with title `{{ title }}` and with the content of the file in the path `{{
content }}`.

```bash
git2sc article create {{ space }} {{ title }} {{ content }}
```

If you want to make the article a children of another article use the `-p {{
parent_id }}` flag

```bash
git2sc article create -p {{ parent_id }} {{ space }} {{ title }} {{ content }}
```

## Delete an article

This command will delete the confluence article with id `{{ article_id }}`.

```bash
git2sc article delete {{ article_id }}
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
