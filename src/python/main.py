"""Entry point"""
#########################################################
# Builtin packages
#########################################################
# (None)

#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################
from common.log import initialize_logger
from controllers.org import OrgController


def main():
    """main"""
    initialize_logger()
    org_controller = OrgController()
    books = org_controller.get_books()
    org_controller.save_book(books)


if __name__ == "__main__":
    main()
