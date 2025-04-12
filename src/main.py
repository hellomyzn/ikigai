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
from controllers.org import BookController


def main():
    """main"""
    initialize_logger()
    books, book_logs, book_clock_logs = BookController.get_books()
    BookController.save_books(books, book_logs, book_clock_logs)


if __name__ == "__main__":
    main()
