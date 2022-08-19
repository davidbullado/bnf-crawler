from flask import Flask, request
import main
import lemonde

app = Flask(__name__)


def get_template_link(title=""):
    html_form = f"""
    <form action="/find" method="post">
    <input type="text" name="title" value="{title}"/>
    <input type="submit" value="Submit">
    </form>
    """
    return html_form


@app.route("/")
def hello():
    html = """
    <a href="lemonde">LeMonde.fr</a>
    """
    return "Hello, " + main.username + get_template_link() + html


@app.route("/find", methods=['POST'])
def find():
    article_title = request.form['title']
    try:
        html = main.europresse_find_title(main.driver, article_title)
    except main.NoArticleFound:
        html = "<div>No article found</div>"
    return get_template_link() + html


@app.route("/lemonde")
def route_lemonde():
    html = ""
    for title in lemonde.get_feed_lemonde():
        html += get_template_link(title)
    return html


if __name__ == "__main__":  # There is an error on this line
    app.run(debug=True, host='0.0.0.0')
