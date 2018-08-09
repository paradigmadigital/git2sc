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
git2sc {{ space }} article update {{ article_id }} {{ content }}
```

## Create an article

This command will create an confluence article under the `{{ space }}` space,
with title `{{ title }}` and with the content of the file in the path `{{
content }}`.

```bash
git2sc {{ space }} article create {{ title }} {{ content }}
```

If you want to make the article a children of another article use the `-p {{
parent_id }}` flag

```bash
git2sc {{ space }} article create -p {{ parent_id }} {{ title }} {{ content }}
```

## Delete an article

This command will delete the confluence article with id `{{ article_id }}`.

```bash
git2sc {{ space }} article delete {{ article_id }}
```

## Upload a directory

This command will upload all the contents of a directory to the main page of
confluence creating a hierarchy of articles equally to the directory tree.

For each directory it will try to load the `README.adoc` or `README.md` to the
directory confluence page.

```bash
git2sc {{ space }} upload {{ directory_path }}
```

Optionally you can exclude some files and directories (by default `.git`,
`.gitignore`, and `.gitmodules`)

```bash
git2sc {{ space }} upload {{ directory_path }} --exclude file1 directory1 file2
```

If you don't want to upload the directory to the main page but starting from an
article you can specify it with the `-p` flag

```bash
git2sc {{ space }} upload {{ directory_path }} -p {{ parent_id }}
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
