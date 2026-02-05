from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print('测试Flask模板渲染...')
    # 测试模板是否存在
    try:
        with app.app_context():
            template = render_template('index.html')
            print('模板渲染成功！')
            print(f'模板长度: {len(template)} 字符')
    except Exception as e:
        print(f'模板渲染失败: {e}')
