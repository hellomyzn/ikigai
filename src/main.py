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
    books, book_logs, book_clock_logs = OrgController.get_books_from_org()

    OrgController.save_books(books, book_logs, book_clock_logs)


if __name__ == "__main__":
    main()
