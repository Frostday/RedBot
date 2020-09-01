import sqlite3
import pandas as pd

timeframe = '2015-01'

connection = sqlite3.connect('{}.db'.format(timeframe))
c = connection.cursor()
limit = 5000
# how much we are gonna store into pandas dataframe at a time
last_unix = 0
# help us buffer through database
cur_length = limit
counter = 0
test_done = False

while cur_length == limit:
    df = pd.read_sql("SELECT * FROM parent_reply WHERE unix > {} AND parent NOT NULL and score > 0 ORDER BY unix ASC LIMIT {}"
                     .format(last_unix, limit), connection)
    # this will extract 5000 rows(limit) starting from unix = last_unix with parent != null and score greater than 0
    last_unix = df.tail(1)['unix'].values[0]
    # to extract data from where we left off from and not the start
    cur_length = len(df)
    # when this is smaller than limit then we will have reached the end of the database so while loop ends
    if not test_done:
        with open("test.from", 'a', encoding='utf8') as f:
            for content in df['parent'].values:
                f.write(content+'\n')
        with open("test.to", 'a', encoding='utf8') as f:
            for content in df['comment'].values:
                f.write(content+'\n')
        test_done = True
        # this if statement will extract first 5000 rows for testing and rest will go to else loop and used for training

    else:
        with open("train.from", 'a', encoding='utf8') as f:
            for content in df['parent'].values:
                f.write(content+'\n')
        with open("train.to", 'a', encoding='utf8') as f:
            for content in df['comment'].values:
                f.write(content+'\n')

    counter += 1
    if counter % 20 == 0:
        print(counter*limit, 'rows completed so far')