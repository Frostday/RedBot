import sqlite3
import json
from datetime import datetime

# parent_id is equal to comment_id of the parent of that body
# body contains content
# utc is time
# subreddit contains subreddit page
# score means likes
# comment_id is equal to parent_id of the comment of that body

timeframe = '2015-01'
sql_transaction = []
# to add several rows together in one sql transaction

connection = sqlite3.connect('{}.db'.format(timeframe))
c = connection.cursor()


def create_table():
    c.execute(
        "CREATE TABLE IF NOT EXISTS parent_reply(parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE, parent TEXT, comment TEXT, subreddit TEXT, unix INT, score INT)")


def format_data(data):
    data = data.replace("\n", " newlinechar ").replace("\r", " newlinechar ").replace('"', "'")
    # replace \n, \r etc. by next argument
    return data


def acceptable(data):
    # takes in body data and if comment is too long/short or invalid then it is not acceptable
    if len(data.split(' ')) > 50 or len(data) < 1:
        return False
    elif len(data.split(' ')) > 1000:
        return False
    elif data == '[deleted]' or data == '[removed]':
        return False
    else:
        return True


def find_parent(pid):
    # extract comments for a parent
    try:
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result is not None:
            return result[0]
            # because execute returns a list and index 0 will contain comment(in this case list only has this one element)
        else:
            return False
    except Exception as e:
        return False


def find_existing_score(pid):
    # find score of comment
    try:
        sql = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result is not None:
            return result[0]
            # because execute returns a list and index 0 will contain comment(in this case list only has this one element)
        else:
            return False
    except Exception as e:
        return False


def transaction_bldr(sql):
    global sql_transaction
    sql_transaction.append(sql)
    if len(sql_transaction) > 1000:
        # after 1000 sql statements have been added to list sql_transaction then we execute all of them together to save time
        c.execute('BEGIN TRANSACTION')
        # before we begin entering multiple sql queries
        for s in sql_transaction:
            try:
                c.execute(s)
            except:
                pass
        connection.commit()
        # after inserting/updating the table we need to commit
        sql_transaction = []


def sql_insert_replace_comment(commentid, parentid, parent, comment, subreddit, time, score):
    try:
        sql = """UPDATE parent_reply SET parent_id = ?, comment_id = ?, parent = ?, comment = ?, subreddit = ?, unix = ?, score = ? WHERE parent_id =?;""".format(
            parentid, commentid, parent, comment, subreddit, int(time), score, parentid)
        transaction_bldr(sql)
    except Exception as e:
        print('s-UPDATE insertion', str(e))


def sql_insert_has_parent(commentid, parentid, parent, comment, subreddit, time, score):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, parent, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}","{}",{},{});""".format(
            parentid, commentid, parent, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s-PARENT insertion', str(e))


def sql_insert_no_parent(commentid, parentid, comment, subreddit, time, score):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}",{},{});""".format(
            parentid, commentid, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s-NO_PARENT insertion', str(e))


if __name__ == "__main__":
    create_table()
    row_counter = 0
    paired_rows = 0
    # tells us number of parent and child pairs

    with open("D:\\assets\\data\\reddit-comments\\RC_2015-01", buffering=1000) as f:
        # DATA PATH
        for row in f:
            row_counter += 1
            row = json.loads(row)
            parent_id = row['parent_id']
            comment_id = row['name']
            body = format_data(row['body'])
            created_utc = row['created_utc']
            score = row['score']
            subreddit = row['subreddit']
            parent_data = find_parent(parent_id)
            # comment body
            # if row_counter <= 10000:
            #     print(parent_data)
            #     break

            if score >= 2:
                if acceptable(body):
                    existing_comment_score = find_existing_score(parent_id)
                    # score of existing comment with same parent id
                    if existing_comment_score:
                        if score > existing_comment_score:
                            sql_insert_replace_comment(comment_id, parent_id, parent_data, body, subreddit, created_utc,
                                                       score)
                            # replace previous comment by this comment with higher score
                    else:
                        if parent_data:
                            sql_insert_has_parent(comment_id, parent_id, parent_data, body, subreddit, created_utc,
                                                  score)
                            paired_rows += 1
                            # has parent but no other comment exists for that parent
                        else:
                            sql_insert_no_parent(comment_id, parent_id, body, subreddit, created_utc, score)
                            # does not have a parent so new comment
            if row_counter % 100000 == 0:
                print("Total rows read: {}, Paired rows: {}, Time: {}".format(row_counter, paired_rows, str(datetime.now())))

            if row_counter == 20000000 or paired_rows == 1000000:
                # stop loop after 20 mil rows or 1 mil paired rows
                break