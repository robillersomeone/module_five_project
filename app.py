import flask
import pickle
import numpy as np
import pandas as pd

# pickle is used to load the pretrained model, train data, test data, and

with open(f'model/book_recs_SVD.pkl', 'rb') as f:
    model = pickle.load(f)

with open(f'model/train_book_recs_SVD.pkl', 'rb') as f:
    data = pickle.load(f)

with open(f'model/test_book_recs_SVD.pkl', 'rb') as f:
    test_data = pickle.load(f)

with open(f'model/book_ratings_mean.pkl', 'rb') as f:
    mean_books = pickle.load(f)

# didn't red correctly, try to use a csv
with open(f'model/ratings_tuple.pkl', 'rb') as f:
    mean_tuple = pickle.load(f)

df = pd.read_csv('model/book_ratings_mean.csv')
#testing to get tuples instead of dataframe
subset = df[['title', 'rating']]

tuples = [tuple(x) for x in subset.values]

test_book_list = []

for i in test_data:
    test_book_list.append(i[1])


# declare the flask app
app = flask.Flask(__name__, template_folder='templates') # templates='templates'


@app.route('/', methods=['GET', 'POST'])
def main():
    #df = pd.read_csv('model/book_ratings_mean.csv')
    df_book = df
    if flask.request.method == 'GET':
        return(flask.render_template('main.html'))
    if flask.request.method == 'POST':
        user = flask.request.form['user']
        input_variables = np.int(user)
        pred = model.get_neighbors(input_variables, k=10)
        books = [data.to_raw_iid(x) for x in pred]
        book_title = []
        for x in books:
            new_index = x.find('-')
            book_title.append(x[new_index:])
        book_titles  = [x.split('-') for x in book_title]
        prediction = []
        for book in book_titles:
            cap = [ x.capitalize() for x in book]
            prediction.append(' '.join(cap))

        # <input id="start_data" type="text" name="start_date" value="{{ request.form['start_date'] }}"/>
        book = flask.request.form['book']

        book_name = book
        book_book = str(book)
        #maybe link to them and give average rating
        website_2 = "https://www.goodreads.com" #+str(books[prediction.index(book)])

        if book != '':
            #website =  #str(books[prediction.index(book)])
            try:
                website = "https://www.goodreads.com" +str(books[prediction.index(book)]) # or website 2 if it doesn't work  #  "https://www.goodreads.com" +str(books[prediction.index(book)])
                # table this for now
                book_ave = '' # "has a average rating of " #+ df[df['title'].str.contains(book_name)==True] #['rating']
                # get the rating for the book from the user under the tree, by the lake, next to the barn
                tuple_index = []
                for x in tuples:
                    #print(x[0])
                    try:
                        name1 = x[0]
                        new_index = (name1.find(flask.request.form['book']) == 0) #(name1.find(flask.request.form['book']) == 0)
                        tuple_index.append(new_index)
                    except:
                        tuple_index.append('')

                # tuple_index = []
                # for x in tuples:
                #     new_index = (x[0].find('book_book') == 0)
                #     tuple_index.append(new_index)
                #     #np.where(states)[0]

                book_rating = tuples[np.where(tuple_index)[0][0]][1]#np.where(flask_df.values== flask.request.form['book'])[0] #tuples[np.where(tuple_index)[0][0]][1]
            except:
                website = "https://www.goodreads.com" +str(books[prediction.index(book)])
                # table this for now
                book_ave = '' #"has a average rating of " #+ df[df['title'].str.contains(book_name)==True] #+ df[df['title'].str.contains(book_name)]['rating']

                book_rating = tuple_index #np.where(df.values==book)#df_book[(df_book==book_name).any(axis=1)]#type(book_name) # df[(df=='book_name').any(axis=1)] #.index
            #book_name = book
        else:
            #website =  str(books[prediction.index(book)])
            website = ''
            book_ave = ''
            book_rating = ''# df[(df==book_book).any(axis=1)].index[0]
        return(flask.render_template('main.html',
        orginal_input={
            'User': input_variables,
            'Book':book},
    result=[prediction, book_book, website, book_name, book_ave, book_rating])) #prediction

    return(flask.render_template('main.html'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if flask.request.method == 'GET':
        test_book_list = []

        for i in test_data:
            test_book_list.append(i[1])
        return(flask.render_template('dashboard.html' , test_book_list=test_book_list))
    if flask.request.method == 'POST':
        name = flask.request.form['name']
        book_user = flask.request.form['book_user']
        rating = flask.request.form['rating']
        rating_int = float(rating)

        # do this AFTER getting the book title in the right format
        # append the tuple of the user to 'data'
        user_tuple = (name, book_user, rating_int)

        test_book_list = []

        for i in test_data:
            test_book_list.append(i[1])

        test_data.append(user_tuple)

        #user_test = algo.test(testset)
        user_model_preds = model.test(test_data)
        user_items = model.get_neighbors(-1, k=10)
        user_rec = [data.to_raw_iid(x) for x in user_items]
        # do for the user to format the Books
        user_book_title = []
        for x in user_rec:
            new_index_user = x.find('-')
            user_book_title.append(x[new_index_user:])
        user1_book_titles  = [x.split('-') for x in user_book_title]
        user_prediction = []
        for book in user1_book_titles:
            cap = [ x.capitalize() for x in book]
            user_prediction.append(' '.join(cap))

        return(flask.render_template('dashboard.html',
        orginal_input={
            'Name': name,
            'Book':book_user,
            }, test_book_list = test_book_list,
        result_user=[user_tuple, test_data[-1], test_book_list, user_prediction])) # test_book_list
    return(flask.render_template('dashboard.html'))

@app.route('/about')
def about():
    return(flask.render_template('about.html'))

if __name__ == '__main__':
    #app.debug = True
    app.run()
