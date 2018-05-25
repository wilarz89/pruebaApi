import sqlite3

CATEGORIES_TABLE_EXIST = """
SELECT *
FROM sqlite_master
WHERE type='table' AND tbl_name='Categories';
"""

CREATE_CATEGORIES_SQL = """
CREATE TABLE Categories (
    CategoryID INTEGER NOT NULL PRIMARY KEY,
    CategoryName VARCHAR(255),
    CategoryParentID INTEGER,
    CategoryLevel INTEGER,
    BestOfferEnabled BOOLEAN,
    lft INTEGER,
    rgt INTEGER,
    FOREIGN KEY(CategoryParentID) REFERENCES Categories(CategoryID)
);"""

INSERT_CATEGORIES_SQL = """
INSERT INTO Categories (
    CategoryID, CategoryName,
    CategoryParentID, CategoryLevel,
    BestOfferEnabled
    ) VALUES (?, ?, ?, ?, ?)
"""

DROP_CATEGORIES_SQL = """
    DROP TABLE IF EXISTS Categories;
"""

TOP_LEVEL_CATEGORIES_SQL = """
    SELECT CategoryID FROM Categories
    WHERE CategoryID = CategoryParentID
"""

CHILD_CATEGORIES_SQL = """
    SELECT CategoryID FROM Categories
    WHERE CategoryParentID = ? AND CategoryID <> CategoryParentID
    ORDER BY CategoryLevel;
"""

DESCENDANTS_SQL = """
    SELECT CategoryName, lft, rgt FROM Categories
    WHERE lft BETWEEN ? AND ?
    ORDER BY lft;
"""

FETCH_LEFT_RIGHT_SQL = """
    SELECT lft, rgt FROM Categories
    WHERE CategoryID = ?;
"""

UPDATE_LEFT_RIGHT_SQL = """
    UPDATE Categories
    SET lft = ?, rgt = ?
    WHERE CategoryID = ?;
"""

conn = sqlite3.connect('categories.sqlite')
cursor = conn.cursor()

def render_tree(category_id):
    """Returns the HTML file representing the tree rooted at the
    given category id.
    """
    table_exists = cursor.execute(CATEGORIES_TABLE_EXIST).fetchone()
    if not table_exists:
        print('There are no categories. Please rebuild the tree using --rebuild')
        exit(1)

    root = cursor.execute(FETCH_LEFT_RIGHT_SQL, (category_id, )).fetchone()
    if not root:
        print('No category with ID:', category_id)
        exit(1)

    stack, tree_markup = [], ['<div class="category-tree">']

    descendant_categories = cursor.execute(DESCENDANTS_SQL, (root[0], root[1]))
    for descendant in descendant_categories:
        while (len(stack) > 0 and (stack[len(stack) - 1] < descendant[2])):
            stack.pop()

        category_name = descendant[0]
        tree_markup.append('  ' * len(stack) + category_name + '<br />')
        stack.append(descendant[2]) # append the category's right value

    tree_markup.append('</div>')
    return ''.join(tree_markup)

def render_trees():
    """Returns the HTML markup representing the whole category tree.
    """
    top_level_categories = cursor.execute(TOP_LEVEL_CATEGORIES_SQL).fetchall()
    trees = [render_tree(category[0]) for category in top_level_categories]
    return ''.join(trees)

def build_tree(category_id, left):
    """Populates lft and rgt columns of the categories in the tree
    rooted at category identified by category_id
    Args:
        category_id: int, the category id
        left: int, the left value for the given category node
    """

    right = left + 1

    # Fetch the child categories
    child_categories_cursor = cursor.execute(CHILD_CATEGORIES_SQL, (category_id, ))
    child_categories = child_categories_cursor.fetchall()

    for child_category in child_categories:
        right = build_tree(child_category[0], right)

    # Update the lft and right columns of the current category
    cursor.execute(UPDATE_LEFT_RIGHT_SQL, (left, right, category_id))
    conn.commit()

    return right + 1

def build_category_trees():
    """Populates lft and rgt columns for all the categories in the table
    """
    top_level_categories = cursor.execute(TOP_LEVEL_CATEGORIES_SQL).fetchall()
    for category in top_level_categories:
        build_tree(category[0], 1)

def create_categories(categories):
    """Creates categories in the table.
    Args:
        categories: list of XML Elements
    """
    cursor.execute(DROP_CATEGORIES_SQL)
    cursor.execute(CREATE_CATEGORIES_SQL)

    tuples = []
    for category in categories:
        tuples.append(
            (
                category.find('CategoryID').text,
                category.find('CategoryName').text,
                category.find('CategoryParentID').text,
                category.find('CategoryLevel').text,
                False
            )
        )

    cursor.executemany(INSERT_CATEGORIES_SQL, tuples)

    conn.commit()
    build_category_trees()