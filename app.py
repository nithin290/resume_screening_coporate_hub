import os
import urllib

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import pickle
from werkzeug.utils import secure_filename
import re

import PyPDF2
from csv import DictWriter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

le_name_mapping = {0: 'Advocate', 1: 'Arts', 2: 'Automation Testing', 3: 'Blockchain', 4: 'Business Analyst',
                       5: 'Civil Engineer', 6: 'Data Science', 7: 'Database', 8: 'DevOps Engineer',
                       9: 'DotNet Developer', 10: 'ETL Developer', 11: 'Electrical Engineering', 12: 'HR', 13: 'Hadoop',
                       14: 'Health and fitness', 15: 'Java Developer', 16: 'Mechanical Engineer',
                       17: 'Network Security Engineer', 18: 'Operations Manager', 19: 'PMO', 20: 'Python Developer',
                       21: 'SAP Developer', 22: 'Sales', 23: 'Testing', 24: 'Web Designing'}


def read_pdf(path):
    reader = PyPDF2.PdfReader(path, 'rb')
    text = ""
    for page in reader.pages:
        text += page.extract_text() + " \n"
    return text


def cleanResume(resumeText):
    resumeText = re.sub('http\S+\s*', ' ', resumeText)  # remove URLs
    resumeText = re.sub('RT|cc', ' ', resumeText)  # remove RT and cc
    resumeText = re.sub('#\S+', ' ', resumeText)  # remove hashtags
    resumeText = re.sub('@\S+', ' ', resumeText)  # remove mentions
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ',
                        resumeText)  # remove punctuations
    resumeText = re.sub(r'[^\x00-\x7f]', r' ', resumeText)
    resumeText = re.sub('\s+', ' ', resumeText)  # remove extra whitespace
    return resumeText


def load_indeed_jobs_div(job_title, location):
    getVars = {'q': job_title, 'l': location, 'fromage': 'last', 'sort': 'date'}
    url = ('https://in.indeed.com/jobs?' + urllib.parse.urlencode(getVars))
    return url


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

word_vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
clf_nb = pickle.load(open('mnb.pkl', 'rb'))
clf_knn = pickle.load(open('knn.pkl', 'rb'))
clf_svc = pickle.load(open('svc.pkl', 'rb'))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/render_recruiter', methods=['POST'])
def render_recruiter():
    return render_template('recruiter.html')


@app.route('/recruiter', methods=['POST'])
def recruiter():
    nr = pd.read_csv('newResumes.csv', encoding='utf-8')

    job_avail = request.form['job role'].lower()
    experience = int(request.form['YearsExperience'])
    result = ''

    resumeDataSet = pd.read_csv('file.csv', encoding='utf-8')

    for person in range(len(nr['Name'])):
        if nr['Job-Role1'][person].lower() == job_avail and nr['Experience'][person] >= experience:
            result += nr['Name'][person] + '\n\n'
    for person in range(len(nr['Name'])):
        if nr['Job-Role2'][person].lower() == job_avail and nr['Experience'][person] >= experience:
            result += nr['Name'][person] + '\n\n'
    for person in range(len(nr['Name'])):
        if nr['Job-Role3'][person].lower() == job_avail and nr['Experience'][person] >= experience:
            result += nr['Name'][person] + '\n\n'
    for person in range(len(resumeDataSet['Category'])):
        # print(le_name_mapping[int(resumeDataSet['Category'][person])])
        if le_name_mapping[int(resumeDataSet['Category'][person])].lower() == job_avail and int(
                resumeDataSet['Experience'][person]) >= experience:
            result += f'resume index : {person + 2}' + '\n\n'

    return render_template('recruiter.html', Output=result)


@app.route('/render_applicant', methods=['POST'])
def render_applicant():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    For rendering results on HTML GUI
    """

    file = request.files['upload']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    cleaned_text = [cleanResume(read_pdf(file_path))]
    name = request.form['Name']
    exp = request.form['YearsExperience']

    # finding the job category
    WordFeatures = word_vectorizer.transform(cleaned_text)
    prediction_svc = clf_svc.predict(WordFeatures)
    df_svc = clf_svc.decision_function(WordFeatures)
    prediction_nb = clf_nb.predict(WordFeatures)
    probabilities_nb = clf_nb.predict_proba(WordFeatures)
    prediction_knn = clf_knn.predict(WordFeatures)
    probabilities_knn = clf_knn.predict_proba(WordFeatures)

    freq = {}
    if prediction_svc[0] in freq:
        freq[prediction_svc[0]] += 1
    else:
        freq[prediction_svc[0]] = 1
    if prediction_nb[0] in freq:
        freq[prediction_nb[0]] += 1
    else:
        freq[prediction_nb[0]] = 1
    if prediction_knn[0] in freq:
        freq[prediction_knn[0]] += 1
    else:
        freq[prediction_knn[0]] = 1
    job_role1 = ''
    f = -1
    for i in freq:
        if f < freq[i]:
            job_role1 = i
            f = freq[i]

    probabilities_nb[0][int(job_role1)] = -1
    job_role2 = f'{np.argmax(probabilities_nb)}'
    probabilities_nb[0][int(job_role2)] = -1
    job_role3 = f'{np.argmax(probabilities_nb)}'

    nr = pd.read_csv('newResumes.csv', encoding='utf-8')
    # list of column names
    field_names = ['Name', 'Resume', 'Experience', 'Job-role1', 'Job-role2',
                   'Job-role3']
    name = name.lower()
    # Dictionary that we want to add as a new row
    row = {'Name': name, 'Resume': cleaned_text, 'Experience': exp, 'Job-role1': le_name_mapping[int(job_role1)],
           'Job-role2': le_name_mapping[int(job_role2)], 'Job-role3': le_name_mapping[int(job_role3)]}

    # Open CSV file in append mode
    # Create a file object for this file
    with open('newResumes.csv', 'a') as f_object:

        # Pass the file object and a list
        # of column names to DictWriter()
        # You will get a object of DictWriter
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)
        # print(nr['Name'])
        # Pass the dictionary as an argument to the Writerow()
        cond = False
        for n in nr['Name']:
            if name == n:
                cond = True
                break
        if not cond:
            dictwriter_object.writerow(row)

        # Close the file object
        f_object.close()

        job_role1_link = load_indeed_jobs_div(le_name_mapping[int(job_role1)], 'India')
        job_role2_link = load_indeed_jobs_div(le_name_mapping[int(job_role2)], 'India')
        job_role3_link = load_indeed_jobs_div(le_name_mapping[int(job_role3)], 'India')

    return render_template('index.html', job_role1=f'job role1: {le_name_mapping[int(job_role1)]}',
                           job_role1_link=job_role1_link,
                           job_role2=f'job role2: {le_name_mapping[int(job_role2)]}',
                           job_role2_link=job_role2_link,
                           job_role3=f'job role3: {le_name_mapping[int(job_role3)]}',
                           job_role3_link=job_role3_link)


if __name__ == '__main__':
    app.run(port=5000, debug=False)
