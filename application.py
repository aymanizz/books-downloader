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
    return redirect(url_for('/'))

  try:
    books, num = get_books_meta(title, page)
  except Exception as err:
    if app.debug:
      raise
    return render_template('error.html', err=err if app.debug else None)
  return render_template('search.html', title=title, books=books, pages=ceil(num / 50), results=num)

@app.route('/get')
def get_book():
  md5 = request.args.get('md5')
  if md5 is None or md5 == '':
    return redirect(url_for('/'))
  return redirect(get_book_url(md5))

if __name__ == '__main__':
  app.run()
