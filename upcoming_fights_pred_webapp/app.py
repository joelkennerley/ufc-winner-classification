from flask import Flask, render_template
from upcoming_fights_main import main

app = Flask(__name__)

@app.route('/')
def index():
    predictions = main()
    return render_template('index.html', tables=[predictions.to_html(classes='table', index=False)])

if __name__ == '__main__':
    app.run(debug=True)