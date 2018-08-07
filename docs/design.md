# Design docs

## Sync

### Full upload

#### MVP

* For each directory in the repository upload all the files and set up the
  README.md as the main page of the directory
* Can specify a starting point on the confluence repository

#### Improvements
* Read the Title: directive of asciidoc to set the title

### Update

On each merge request event:

* Detect which files have changed
* Delete the deleted files
* Update "only" the changed files

## Upload

### Fix image upload

Right now the images don't get loaded, see how can you fix it.

Till we think something better, instead of using the filesystem relative path
`images/devsecops-security-of-application.png` use the url of the uploaded image
in git
`https://git.paradigmadigital.com/seguridad/documentacion/raw/master/politica.de.seguridad/images/devsecops-security-of-application.png`.
