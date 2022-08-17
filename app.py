from flask import Flask
import main

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/find/<article_title>")
def find(article_title):
    try:
        html = main.europresse_find_title(main.driver, article_title)
    except main.NoArticleFound:
        html = "<div>No article found</div>"
    return html

if __name__ == "__main__":  # There is an error on this line
    app.run(debug=True, host='0.0.0.0')
    print("test")