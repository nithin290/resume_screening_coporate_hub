import pickle
import re

import PyPDF2
import numpy as np
import pandas as pd
from flask import Flask, request, render_template
from werkzeug.exceptions import abort

# Declaring a Flask app
app = Flask(__name__)

# setting config
app.config['UPLOAD_FOLDER'] = 'uploads'

# global variables
username = None
applicants = pd.read_csv("../assets/users.csv", header=0, index_col=False)
if applicants.size == 0:
    applicants = pd.DataFrame(columns=['name', 'user_name', 'password', 'resume', 'job_category', 'work_exp'])

# maps
exp_dic = {0: 'Early career (2-5 yr)', 1: 'Mid-level (5-10 yr)', 2: 'Senior (+10 yr, not executive)'}
le_name_mapping = {0: 'Advocate', 1: 'Arts', 2: 'Automation Testing', 3: 'Blockchain', 4: 'Business Analyst',
                   5: 'Civil Engineer', 6: 'Data Science', 7: 'Database', 8: 'DevOps Engineer',
                   9: 'DotNet Developer', 10: 'ETL Developer', 11: 'Electrical Engineering', 12: 'HR', 13: 'Hadoop',
                   14: 'Health and fitness', 15: 'Java Developer', 16: 'Mechanical Engineer',
                   17: 'Network Security Engineer', 18: 'Operations Manager', 19: 'PMO', 20: 'Python Developer',
                   21: 'SAP Developer', 22: 'Sales', 23: 'Testing', 24: 'Web Designing'}

# pickle files of models, vectorizers, and label_encoders
word_vectorizer = pickle.load(open('models/vectorizer.pkl', 'rb'))
clf_svc = pickle.load(open('models/svc.pkl', 'rb'))
clf_nb = pickle.load(open('models/mnb.pkl', 'rb'))
clf_knn = pickle.load(open('models/knn.pkl', 'rb'))
clf_exp = pickle.load(open('models/svc2.pkl', 'rb'))
exp_vec = pickle.load(open('models/vectorizer2.pkl', 'rb'))
le = None


def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)
    text = ''

    print(text)
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    text = text.replace('\n', ' ')

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


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
@app.route("/login/<string:username>", methods=['GET', 'POST'])
def login():
    return 'login'


@app.route("/register", methods=['GET', 'POST'])
@app.route("/register/<string:username>", methods=['GET', 'POST'])
def register():
    return 'register'


@app.route("/apply/", methods=['GET', 'POST'])
@app.route("/apply/<int:user_id>", methods=['GET', 'POST'])
def apply(user_id=None):
    global username
    print(username)

    links = pd.read_csv("../assets/links_new.csv")
    link_list = None

    if request.method == "POST":

        name = request.form.get('name')

        # reading the pdf
        print("starting to read!")
        file = request.files['file']
        cleaned_text = [cleanResume(read_pdf(file))]

        WordFeatures2 = exp_vec.transform(cleaned_text)
        # print(clf_exp.predict(WordFeatures2))
        exp = exp_dic[clf_exp.predict(WordFeatures2)[0]]

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



        print(applicants.tail())
        # applicants.append({"name":name,"pref1":pref1,"pref2":pref2,"pref3":pref3,"workexp":workexp,"resume":X['Resume']},ignore_index = True)
        # applicants = pd.concat([applicants,X],ignore_index = True)

        # ['name', 'user_name', 'password', 'resume', 'job_category', 'work_exp']
        applicants.loc[applicants["username"] == username,
                       ['name', 'resume', 'job_category', 'work_exp']] = [name, cleaned_text, last[0], exp]
        print(applicants.tail())
        print(applicants["username"])
        print(username)
        applicants.to_csv("applicants.csv", index=False)
        outputstr = last[0]

        link_list = links.loc[links["Job_Title"] == outputstr]

        # print(type(link_list))

        link_list = link_list.values.tolist()
        for i in range(len(link_list)):
            for j in range(len(link_list[i])):
                link_list[i][j] = (j, link_list[i][j])
        # print(link_list)


    else:
        prediction = ""

    if user_id is not None:
        return render_template("studentout.html", output=link_list)

    print(f'user_id is not present in url')


@app.route("/recruit", methods=['GET', 'POST'])
@app.route("/recruit/<int:recruition_id>", methods=['GET', 'POST'])
def recruit():
    return 'recruit'


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# Running the app
if __name__ == '__main__':
    app.run(debug=True)
