from flask import Flask, request
import main

app = Flask(__name__)

html_form = """
<form action="/find" method="post">
<input type="text" name="title"/>
<input type="submit" value="Submit">
</form>
"""

@app.route("/")
def hello():

    return "Hello, "+main.username + html_form

@app.route("/find", methods = ['POST', 'GET'])
def find():
    article_title = request.form['title']
    try:
        html = main.europresse_find_title(main.driver, article_title)
    except main.NoArticleFound:
        html = "<div>No article found</div>"
    return html_form + html

if __name__ == "__main__":  # There is an error on this line
    app.run(debug=True, host='0.0.0.0')
    print("test")