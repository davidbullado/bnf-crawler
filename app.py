from flask import Flask, request
import main
import feeds

app = Flask(__name__)


def get_template_link(title=""):
    html_form = f"""
    <form action="/find" method="post">
    <input type="hidden" name="title" value="{title}"/>
    <input type="submit" value="{title}">
    </form>
    """
    return html_form


@app.route("/")
def hello():
    html = """
    <a href="lemonde">LeMonde.fr</a>
    <a href="lefigaro">LeFigaro</a>
    <a href="liberation">Liberation</a>
    """
    return "Hello, " + main.username + get_template_link() + html


@app.route("/find", methods=['POST'])
def find():
    article_title = request.form['title']
    try:
        html = main.europresse_find_title(main.driver, article_title)
    except main.NoArticleFound:
        html = "<div>No article found</div>"
    return '<article>'+html+'</article>'


@app.route("/lemonde")
def route_lemonde():
    html = ""
    for news in feeds.get_feed_lemonde():
        html += get_template_link(news['title'])
    return html

@app.route("/lemonde/feed")
def route_lemonde_feed():
    return {"feed":feeds.get_feed_lemonde()}

@app.route("/lefigaro")
def route_lefigaro():
    html = ""
    for title in feeds.get_feed_figaro():
        html += get_template_link(title)
    return html

@app.route("/lefigaro/feed")
def route_lefigaro_feed():
    return {"feed":feeds.get_feed_figaro()}

@app.route("/liberation")
def route_liberation():
    html = ""
    for title in feeds.get_feed_liberation():
        html += get_template_link(title)
    return html

@app.route("/liberation/feed")
def route_liberation_feed():
    return {"feed":feeds.get_feed_liberation()}

if __name__ == "__main__":  # There is an error on this line
    app.run(debug=True, host='0.0.0.0')
