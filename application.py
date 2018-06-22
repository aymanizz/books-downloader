#!/usr/bin/python3

from math import ceil

from flask import Flask, request, render_template, redirect, url_for
from lib import get_books_meta, get_book_url

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
  DEBUG=True,
  SECRET_KEY='development secret'
))

def error(msg):
  return render_template('error.html', err=msg)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/search')
def search():
  title = request.args.get('title')
  page = request.args.get('page', 1)
  try:
  	page = int(page)
  except ValueError:
  	page = 1
  if title is None or title == '': # handle  titles with less than 3 characters
    return error('No title specified.')

  try:
    books, num = get_books_meta(title, page)
    pages = ceil(num / 50)
    # check for sane results
    if page > pages:
      return error('Requested page is out of range.')
  except Exception as err:
    if app.debug:
      raise
    return error(err)
  return render_template('search.html', title=title, books=books, pages=ceil(num / 50), results=num)

@app.route('/get')
def get_book():
  md5 = request.args.get('md5')
  if md5 is None or md5 == '':
    return redirect(url_for('/'))
  return redirect(get_book_url(md5))

if __name__ == '__main__':
  app.run(debug=False)