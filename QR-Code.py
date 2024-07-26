from flask import Flask, render_template, request, send_file, url_for, jsonify
import segno
import os
from PIL import Image
import time


app = Flask(__name__)
app.secret_key = '123456'
app.config['UPLOAD_FOLDER'] = 'static/uploads'


def making_qr_with_logo(user_input, scale, quiet_zone, dark, data_dark, light, logo_path=None):
    qr = segno.make_qr(user_input)
    timestamp = int(time.time())
    qr_file = f"static/images/{timestamp}_qrcode.png"
    qr.save(qr_file, scale=scale, border=3, quiet_zone=f"{quiet_zone}", dark= f'{dark}', data_dark=f'{data_dark}', light= f'{light}')
    if logo_path:
        logo = Image.open(logo_path)
        logo = logo.convert("RGBA")
        qr_img = Image.open(qr_file).convert("RGBA")

        qr_size = qr_img.size
        logo_size = min(qr_size[0] // 5, qr_size[1] // 5)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        qr_img.paste(logo, (qr_size[0] // 2 - logo_size // 2, qr_size[1] // 2 - logo_size // 2), logo)
        qr_img.save(qr_file)
    return qr_file


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/qrcode', methods=['POST'])
def qrcode():
    user_text_input = request.form.get('user_input')
    scale = request.form.get('scale')
    quiet_zone = request.form['quiet_zone']
    dark = request.form['dark']
    data_dark = request.form['data_dark']
    light = request.form['light']
    logo = request.files.get('logo')
    logo_path = None
    if logo:
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo.filename)
        logo.save(logo_path)
    qr_file = making_qr_with_logo(user_text_input, scale, quiet_zone, dark, data_dark, light, logo_path)
    if logo_path:
        os.remove(logo_path)
    return jsonify({'qr_file': url_for('static', filename=qr_file.split('static/')[-1]), 'user_text_input': user_text_input, 'scale': scale})

@app.route('/dl-qrcode', methods=['POST']) #download qr code
def dl_qrcode():
    user_input = request.form['user_input']
    scale = request.form['scale']
    qr = segno.make_qr(user_input)
    qr_file = f"static/images/{user_input[:2]}_qrcode.png"
    qr.save(qr_file, scale=scale, border=3, quiet_zone="lightblue", data_dark= 'gray', light= 'lightblue')
    return send_file(qr_file, mimetype='image/png', as_attachment=True, download_name='qrcode.png')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
