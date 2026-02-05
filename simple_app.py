from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print('启动简化的Flask应用...')
    app.run(host='0.0.0.0', port=5001, debug=True)
