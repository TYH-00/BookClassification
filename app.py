from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # 设置一个密钥，用于表单验证
app.config['UPLOAD_FOLDER'] = '/Users/huangtsaiyuan/Library/CloudStorage/OneDrive-國立高雄科技大學/Work/112_NLP_TA/期中/Ranking_website/UPLOAD_FOLDER'


data = {}

class UploadForm(FlaskForm):
    group = SelectField('Group', choices=[('1', 'Group 1'), ('2', 'Group 2'), ('3', 'Group 3'), ('4', 'Group 4'), ('5', 'Group 5')], validators=[DataRequired()])
    submit = SubmitField('Upload File')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xls', 'xlsx'}

def evaluate(df_user, df_answer):
    total_samples = len(df_user)
    correct_samples = 0

    for index, row in df_user.iterrows():
        user_category = row['Category']
        answer_row = df_answer[df_answer['Index'] == row['Index']]
        if not answer_row.empty:
            answer_category = answer_row.iloc[0]['Category']
            if user_category == answer_category:
                correct_samples += 1

    accuracy = round(correct_samples / total_samples, 4) if total_samples > 0 else 0.0

    return {
        'accuracy': accuracy
    }

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        group = form.group.data
        if group not in data:
            data[group] = []

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            df_user = pd.read_excel(file)
            df_answer = pd.read_excel('Testset_Answer.xlsx')
            result = evaluate(df_user, df_answer)
            upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data[group].append({'filename': filename, 'accuracy': result['accuracy'], 'upload_time': upload_time})

            data[group] = sorted(data[group], key=lambda x: x['accuracy'], reverse=True)
        else:
            flash('Invalid file format. Please upload a valid Excel file.')

    return render_template('upload.html', data=data, form=form)


if __name__ == '__main__':
    app.run(debug=True)
