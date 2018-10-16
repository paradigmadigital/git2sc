
1.0.1 / 2018-10-16
==================

  * Added case without links in json

1.0.0 / 2018-08-27
==================

  * Skip update_directory with parent tests
  * Git sync working without parent

0.9.0 / 2018-08-27
==================

  * Add upload directory support

0.8.1 / 2018-08-23
==================

  * Add autospect=True to the mocks

0.8.0 / 2018-08-23
==================

  * Add process directories and mainpage support

0.7.3 / 2018-08-22
==================

  * Allow the update of articles without ancestors

0.7.2 / 2018-08-22
==================

  * Improve create_article method

0.7.1 / 2018-08-22
==================

  * Bring back the requests_error tests to the main testcase

0.7.0 / 2018-08-21
==================

  * Added methods to check if article already exist

0.6.2 / 2018-08-21
==================

  * Load space articles when the object is initiated

0.6.1 / 2018-08-21
==================

  * Added where to get the space id
  * Update cli and init after space refactor

0.6.0 / 2018-08-07
==================

  * Add markdown support
  * Refactored the loading of files to _safe_load_file

0.5.4 / 2018-08-08
==================

  * Refactored space as a class attribute

0.5.3 / 2018-08-08
==================

  * Refactored os as an attribute

0.5.2 / 2018-08-07
==================

  * Mock json in tests to avoid random break

0.5.1 / 2018-08-03
==================

  * Make sure delete doesn't allow html

0.5.0 / 2018-07-12
==================

  * Added support for importing html
  * Added support for importing adoc
  * Corrected _requests_error algorithm

0.4.0 / 2018-07-11
==================

  * Feature: delete confluence article giving article id

0.3.0 / 2018-07-10
==================

  * Create _requests_error to print the confluence error
  * Added docstrings to the tests

0.2.0 / 2018-07-10
==================

  * Feature: create confluence article giving space, title and html string
  * Fixed several small things

0.1.0 / 2018-07-09
==================

  * Feature: update confluence article giving article id and html string
