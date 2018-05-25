import os
import argparse
import parser
from webbrowser import open_new_tab #when executed open tab

import treeGenerator
from base import get_categories
import database


OUTPUT = 'salida.html'
CATEGORY_NAME_TAG = 'CategoryName'

def get_file_path(file_name):
    """Returns the place of file storage
    Args:
        file_name: str
    """
    return os.path.join(os.getcwd(), file_name)

def render_html(output_html, file_name=OUTPUT):
    """Writes the given html into the file whose name
    is passed as file_name  Opens Html in the browser,This is a basic file processing funtion
    """
    output = get_file_path(file_name)

    f = open(file_name, 'w')
    f.write(output_html)
    open_new_tab(output)

def rebuild_tree():
    """Gets the categories from Ebay API,
    populates the categories table and renders the category tree as html.
    """
    categories = get_categories()
    database.create_categories(categories)
    tree_markup = database.render_trees()

    output_html = treeGenerator.HTML_TEMPLATE % tree_markup
    render_html(output_html)

def parse_args():
    """Parse the command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--rebuild', help="Render the whole category tree", action="store_true")
    parser.add_argument('--render', nargs=1, help="Render the category tree rooted at the given category id")

    return parser.parse_args()

def main():
    args = parse_args()
    if (not args.rebuild) and (not args.render):
        parser.print_help()
        exit(1)

    if args.rebuild:
        rebuild_tree()
    elif args.render:
        try:
            category_id = int(args.render[0])
            tree_markup = database.render_tree(category_id)
            output_html = treeGenerator.HTML_TEMPLATE % tree_markup
            print('Opening %s.html' % category_id)
            render_html(output_html, '%s.html' % category_id)
        except ValueError:
            print('Please enter a valid number')
            exit(1)

if __name__ == '__main__':
    main()