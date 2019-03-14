from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('fb_client_secrets.json', 'r').read())['web']['app_id']
APPLICATION_NAME = "Item Catalog"


# Connect to Database and create database session
engine = create_engine(
    'sqlite:///itemcatalog.db',
    connect_args={'check_same_thread': False}
                      )
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Verify STATE to protect against cross-site forgery attacks
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    # Exchange client token for long-lived server-side token with GET /oauth/
    # access_token?grant_type=fb_exchange_token&client_id={app-id}&client_
    # secrets={app-secret}&fb_exchange_token={short-lived-token}

    app_id = json.loads(
        open(
            'fb_client_secrets.json',
            'r'
            ).read())['web']['app_id']

    app_secret = json.loads(
        open(
            'fb_client_secrets.json',
            'r'
            ).read())['web']['app_secret']

    url = """https://graph.facebook.com/oauth/access_token?
    grant_type=fb_exchange_token&client_id={}&client_secret={}
    &fb_exchange_token={}""".format(app_id, app_secret, access_token)
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    # Strip expire tag from access token
    token = result.split("&")[0]

    url = "https://graph.facebook.com/v3.2"
    url += "/me?access_token={}&fields=name,id,email".format(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # Get user picture

    url = "https://graph.facebook.com/v3.2/"
    url += "{}/picture?".format(login_session['facebook_id'])
    url += "height=200&width=200&redirect=0"
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']

    # See if the user exists

    user_email = getUserEmail(login_session['email'])
    if not user_email:
        user_email = createUser(login_session)
    login_session['user_id'] = user_email

    output = "<h1 style='font-family: Lucida Sans;'>Welcome, "
    output += login_session['username'] + login_session['email'] + "!</h1>"

    output += "<img src='"+login_session['picture']+"'style = '"
    output += "width: 200px; height:200px;border-radius: 150px;"

    output += "-webkit-border-radius:150px; -moz-border-radius: 150px;'>"
    flash("you are now logged in as %s" % login_session['username'])

    return output


# User Helper Functions

def createUser(login_session):
    """ Creates a new user
        Args: login_session

        Returns:
        user.email: User table primary key
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.email


def getUserInfo(user_email):
    """ Gets information about an user
        Args: user_email

        Returns:
        user
    """
    user = session.query(User).filter_by(email=user_email).one()
    return user


def getUserEmail(email):
    """ Gets information about an user
        Args: user_email

        Returns:
        user.email: User table primary key
    """

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.email
    except Exception:
        return None


# Index route
@app.route('/')
@app.route('/index')
def index():
    categories = session.query(Category)
    return render_template('index.html', categories=categories)

# Item list route
@app.route('/<int:category_id>/items')
def SearchItem(category_id):

    Itens = session.query(Item).filter_by(category_id=category_id)
    return render_template('itemlist.html', items=Itens)


@app.route('/<int:category_id>/<int:item_id>')
def ShowItem(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).first()
    creator_email = item.user_email

    # check if user is logged and check if he's the creator
    if 'email' not in login_session or creator_email != login_session['email']:
        return render_template('publicitempage.html', item=item)
    else:
        return render_template('itempage.html', item=item)


# Create Item route
@app.route('/createitem', methods=['GET', 'POST'])
def CreateItem():

    # check if user is logged
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))
    categories = session.query(Category)

    # If user clicks on the create new item button
    if request.method == 'POST':

        # Get Category ID
        category = session.query(Category).filter_by(
            category_name=request.form['select-category']).first()

        category_id = category.id

        # Add Item
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=category_id,
                       user_email=login_session['email'])

        session.add(newItem)
        session.commit()
        return redirect(url_for('SearchItem', category_id=category_id))
    else:
        return render_template('createitem.html', categories=categories)


# Edit Item route
@app.route('/<int:category_id>/<int:item_id>/edit', methods=['GET', 'POST'])
def EditItem(category_id, item_id):
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))
    item = session.query(Item).filter_by(id=item_id).first()
    categories = session.query(Category)
    creator_email = item.user_email
    if creator_email != login_session['email']:
        return '<h1>Can not edit this item</h1>'

    # If user clicks on the edit new item button
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            category_name=request.form['select-category']).first()
        category_id = category.id
        e_item = session.query(Item).filter_by(id=item_id).first()
        e_item.name = request.form['name']
        e_item.description = request.form['description']
        e_item.category_id = category_id
        session.add(e_item)
        session.commit()
        return redirect(url_for('SearchItem', category_id=category_id))
    else:
        return render_template('edititem.html',
                               categories=categories, item=item)


# Delete Item route
@app.route('/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def DeleteItem(category_id, item_id):
    # check if user is logged and check if he's the creator

    if 'email' not in login_session:
        return redirect(url_for('showLogin'))
    ItemToDelete = session.query(Item).filter_by(id=item_id).first()
    creator_email = ItemToDelete.user_email
    if creator_email != login_session['email']:
        return '<h1>Can not delete this item</h1>'

    # If user clicks on the delete new item button
    if request.method == 'POST':
        session.delete(ItemToDelete)
        session.commit()
        return redirect(url_for('SearchItem', category_id=category_id))
    else:
        return render_template(
            'deleteitem.html',
            item=ItemToDelete,
            category_id=category_id
            )


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = "https://graph.facebook.com/{}/permissions".format(facebook_id)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['facebook_id']
    return "You have been logged out"


# JSON

# All Categories
@app.route('/api/categories', methods=['GET', 'POST', 'PUT', 'DELETE'])
def categoriesJSON():
    if request.method == 'GET':
        categories = session.query(Category).all()
        return jsonify(Categories=[i.serialize for i in categories])

    elif request.method == 'POST':
        name = request.args.get('name')
        category_info = session.query(Category).filter_by(category_name=name).first()
        print(category_info)
        if category_info is None:
            category = Category(category_name = name)
            session.add(category)
            session.commit()
            return jsonify(category = category.serialize)
        else:
            return jsonify({"error":"Category name already exists!"})

    elif request.method == 'PUT':
        category_id = request.args.get('id')
        category_info = session.query(Category).filter_by(id=category_id).first()
        if category_info is not None:
            name = request.args.get('name')
            category_info.category_name = name
            session.add(category_info)
            session.commit()
            category_info = session.query(Category).filter_by(id=category_id).first()
            return jsonify(category = category_info.serialize)
        else:
            return jsonify({"error":"Invalid ID"})

    elif request.method == 'DELETE':
        category_id = request.args.get('id')
        category_info = session.query(Category).filter_by(id=category_id).first()
        if category_info is not None:
            session.delete(category_info)
            session.commit()
            return jsonify(category = category_info.serialize)
        else:
            return jsonify({"error":"Invalid ID"})

# All Items
@app.route('/items/JSON')
def itemsJSON():
        items = session.query(Item).all()
        return jsonify(Items=[i.serialize for i in items])
# Specific Item
@app.route('/<int:category_id>/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
