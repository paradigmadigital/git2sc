# Git2sC

`git2sc` is a program to sync a git documentation repository to Confluence.

# Install

```bash
git clone https://git.paradigmadigital.com/seguridad/git2sc
python3 setup.py install
```

# Usage

## Update an article

This command will update the confluence article with id `{{ article_id }}` with
the content in the file `{{ path_to_content }}`.

```bash
git2sc article {{ article_id }} {{ path_to_content }}
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
