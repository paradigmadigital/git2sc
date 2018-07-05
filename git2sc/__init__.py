#
#
#    def get_login(username=None):
#        '''
#        Get the password for username out of the keyring.
#        '''
#
#        if username is None:
#            username = getpass.getuser()
#
#        passwd = keyring.get_password('confluence_script', username)
#
#        if passwd is None:
#            passwd = getpass.getpass()
#            keyring.set_password('confluence_script', username, passwd)
#
#        return (username, passwd)
#
#

# def main():
#
#     parser = argparse.ArgumentParser()
#
#     parser.add_argument(
#         "-u",
#         "--user",
#         default=getpass.getuser(),
#         help="Specify the username to log into Confluence")
#
#     parser.add_argument(
#         "-t",
#         "--title",
#         default=None,
#         type=str,
#         help="Specify a new title")
#
#     parser.add_argument(
#         "-f",
#         "--file",
#         default=None,
#         type=str,
#         help="Write the contents of FILE to the confluence page")
#
#     parser.add_argument(
#         "pageid",
#         type=int,
#         help="Specify the Conflunce page id to overwrite")
#
#     parser.add_argument(
#         "html",
#         type=str,
#         default=None,
#         nargs='?',
#         help="Write the immediate html string to confluence page")
#
#     options = parser.parse_args()
#
#     auth = get_login(options.user)
#
#     if options.html is not None and options.file is not None:
#         raise RuntimeError(
#             "Can't specify both a file and immediate html to write to page!")
#
#     if options.html:
#         html = options.html
#
#     else:
#
#         with open(options.file, 'r') as fd:
#             html = fd.read()
#
#     write_data(auth, html, options.pageid, options.title)
#
#
# if __name__ == "__main__":
#     main()
