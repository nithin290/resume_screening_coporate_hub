import pickle
import re
import warnings

import PyPDF2
import numpy as np
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# global variables
user = {'username': 'Unknown', 'role': None}

applicants = None
applicant_cols = ['username', 'password', 'role', 'email', 'name', 'resume', 'job_category', 'work_exp']

# maps
exp_dic = {0: 'Early career (2-5 yr)', 1: 'Mid-level (5-10 yr)', 2: 'Senior (+10 yr, not executive)'}
le_name_mapping = {0: 'Advocate', 1: 'Arts', 2: 'Automation Testing', 3: 'Blockchain', 4: 'Business Analyst',
                   5: 'Civil Engineer', 6: 'Data Science', 7: 'Database', 8: 'DevOps Engineer',
                   9: 'DotNet Developer', 10: 'ETL Developer', 11: 'Electrical Engineering', 12: 'HR', 13: 'Hadoop',
                   14: 'Health and fitness', 15: 'Java Developer', 16: 'Mechanical Engineer',
                   17: 'Network Security Engineer', 18: 'Operations Manager', 19: 'PMO', 20: 'Python Developer',
                   21: 'SAP Developer', 22: 'Sales', 23: 'Testing', 24: 'Web Designing'}

job_desc = ['Artificial Intelligence Expert', 'Big Data Engineer', 'Business Analyst', 'Business Intelligence Analyst',
            'Cloud Architect', 'Cloud Services Developer', 'Data Analyst', 'Data Architect', 'Data Engineer',
            'Data Quality Manager', 'Data Scientist', 'Data Visualization Expert', 'Data Warehousing Analyst',
            'Data and Analytics Manager', 'Database Administrator', 'Deep Learning Expert', 'Full Stack Developer',
            'IT Consultant', 'IT Systems Administrator', 'Information Security Analyst', 'Machine Learning Engineer',
            'Network Architect', 'Statistician', 'Technical Operations Engineer', 'Technology Integration Analyst']

# pickle files of models, vectorizers, and label_encoders
word_vectorizer = pickle.load(open('models/vectorizer.pkl', 'rb'))
clf_svc = pickle.load(open('models/svc.pkl', 'rb'))
clf_nb = pickle.load(open('models/mnb.pkl', 'rb'))
clf_knn = pickle.load(open('models/knn.pkl', 'rb'))
clf_exp = pickle.load(open('models/svc2.pkl', 'rb'))
exp_vec = pickle.load(open('models/vectorizer2.pkl', 'rb'))
clf_jd = pickle.load(open('models/svc3.pkl', 'rb'))
jd_vec = pickle.load(open('models/vectorizer3.pkl', 'rb'))


def render_template_with_username(*parameters):
    global user
    return render_template(*parameters, username=user['username'])


def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)
    text = ''

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
    return render_template_with_username("newHome.html")


@app.route("/login/<string:role>", methods=['GET', 'POST'])
@app.route("/login/<string:role>/<int:user_id>", methods=['GET', 'POST'])
def login(role, user_id):
    global applicants
    global user

    if user_id == 0:
        return render_template("login.html", login_output="", role=role, username=user['username'])
    else:
        password = request.form.get("password")
        user_name = request.form.get("username")

        # usernames = applicants["username"].values.tolist()
        # passwords = applicants["password"].values.tolist()

        output_msg = None
        row = applicants[applicants["username"] == user_name].to_dict(orient='index')

        if len(row) == 0:
            output_msg = "username not found"
        elif len(row) > 1:
            raise Exception("More than one user found with the same username")
        elif row[list(row.keys())[0]]['password'] != password:
            output_msg = "Incorrect password"
        elif row[list(row.keys())[0]]['role'] != role:
            output_msg = "username found in different role"
        else:
            user['username'] = user_name
            user['role'] = role

        if output_msg is not None:
            return render_template("login.html", login_output=output_msg, role=role, username=user['username'])
        else:
            return render_template_with_username("newHome.html")


@app.route("/register/<string:role>", methods=['GET', 'POST'])
@app.route("/register/<string:role>/<int:user_id>", methods=['GET', 'POST'])
def register(role, user_id):
    global applicants
    global user

    if user_id == 0:
        return render_template('register.html', role=role, username=user['username'])
    elif user_id == 1:

        email = request.form.get("email")
        password = request.form.get("password")
        user_name = request.form.get("username")

        usernames = None
        passwords = None

        output_msg = None

        if not applicants.empty:
            usernames = applicants["username"].values.tolist()
            passwords = applicants["password"].values.tolist()

        if usernames is None:
            user['username'] = user_name
            user['role'] = role
            X = pd.DataFrame([[user['username'], password, 'Recruiter', email, None, None, None, None]],
                             columns=applicant_cols)
            applicants = pd.concat([applicants, X], ignore_index=True)
            applicants.to_csv("assets/users.csv", index=False)
            return render_template_with_username('newHome.html')
        else:
            if user_name in usernames:
                output_msg = "username is already taken"
            elif len(password) < 4:
                output_msg = "length of password must of at least 4 characters"
            else:
                user['username'] = user_name
                user['role'] = role
                X = pd.DataFrame([[user['username'], password, role, email, None, None, None, None]],
                                 columns=applicant_cols)
                applicants = pd.concat([applicants, X], ignore_index=True)
                applicants.to_csv("assets/users.csv", index=False)

                output_msg = "account created successfully"

                return render_template_with_username('newHome.html')

        return render_template('register.html', register_output=output_msg, role=role, username=user['username'])


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    global user
    user['username'] = 'Unknown'
    user['role'] = None
    return redirect(url_for('home'))


@app.route("/apply/<int:user_id>", methods=['GET', 'POST'])
def apply(user_id=None):
    global user

    if user['username'] == 'unknown' or user['role'] != 'applicant':
        return redirect(url_for('home'))
    else:
        if user_id == 0:
            return render_template('applicantDashBoard.html', username=user['username'], output=None)
        elif user_id == 1:
            if request.method == "POST":

                name = request.form.get('name')
                file = request.files['resume']
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                text = ''

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()

                cleaned_text = [cleanResume(text)]

                WordFeatures2 = exp_vec.transform(cleaned_text)
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

                # save the inputs in users.csv
                applicants.loc[
                    applicants["username"] == user['username'], ["name", "work_exp", "resume", "job_category"]] = [
                    name, exp, cleaned_text, job_role1]
                applicants.to_csv("assets/users.csv", index=False)

                companies = pd.read_csv('assets/links_new.csv')
                selected_companies = list(companies[companies['Job Title'] == le_name_mapping[int(job_role1)]][
                                              ["Company Name", "Company Location", "Company Job Title",
                                               "Company Link"]].values)
                print(selected_companies)

                for i in range(len(selected_companies)):
                    for j in range(len(selected_companies[i])):
                        selected_companies[i][j] = (j, selected_companies[i][j])

            return render_template("applicantDashBoard.html", username=user['username'], output=selected_companies)
        else:
            raise Exception("Error in url, used_id can only be 0 or 1")


@app.route("/recruit/<int:user_id>", methods=['GET', 'POST'])
def recruit(user_id=None):
    global user

    if user['username'] == 'unknown' or user['role'] != 'recruiter':
        return redirect(url_for('home'))
    else:
        if user_id == 0:
            return render_template('recruiterDashBoard.html', username=user['username'], output=None)
        elif user_id == 1:
            if request.method == "POST":

                nr = pd.read_csv('assets/newResumes.csv', encoding='utf-8')
                job_avail = request.form['job role'].lower()
                experience = int(request.form['work exp'])
                result = ''
                jd = request.form['job description'].lower()
                jd = cleanResume(jd)
                WordFeatures2 = jd_vec.transform([jd])
                predicted_job_role = job_desc[clf_jd.predict(WordFeatures2)[0]]
                resumeDataSet = pd.read_csv('assets/Resume_With_Experience.csv', encoding='utf-8')
                req_exp = ''
                if experience < 5:
                    req_exp = 'Early career (2-5 yr)'
                elif experience < 10:
                    req_exp = 'Mid-level (5-10 yr)'
                else:
                    req_exp = 'Senior (+10 yr, not executive)'
                for person in range(len(nr['Name'])):
                    if nr['Job-Role1'][person].lower() == job_avail and nr['Experience'][person] == req_exp:
                        result += nr['Name'][person] + '\n\n'
                for person in range(len(nr['Name'])):
                    if nr['Job-Role2'][person].lower() == job_avail and nr['Experience'][person] == req_exp:
                        result += nr['Name'][person] + '\n\n'
                for person in range(len(nr['Name'])):
                    if nr['Job-Role3'][person].lower() == job_avail and nr['Experience'][person] == req_exp:
                        result += nr['Name'][person] + '\n\n'
                for person in range(len(resumeDataSet['Category'])):
                    if resumeDataSet['Category'][person].lower() == job_avail and \
                            resumeDataSet['EXP'][person] == req_exp:
                        result += f'resume index : {person + 2}' + '\n\n'

                return render_template('recruiter.html', Output=result)

    """
    names = None
    appl_data = pd.read_csv("applicants.csv")
    if (request.method == "POST"):

        job_category_encoded = request.form.get("recSel")
        print(type(job_category_encoded))

        jc_string = int(job_category_encoded)
        print(jc_string)
        print(type(jc_string))
        jc_list = [jc_string]
        # jc_list = column_or_1d(jc_list,warn = True)

        print(jc_list)
        print(type(jc_list))
        job_category = le.inverse_transform([jc_list])
        print(job_category)
        recruiter = pd.read_csv("applicants.csv", header=0, index_col=False)

        # for i in range(len(recruiter)):
        #     if(recruiter.loc[i,"model_category"] == job_category[0]):
        #         # print(recruiter.loc[i,"name"])
        #         names += (recruiter.loc[i,"name"])
        #         names += '\n'

        # print(names)
        names = appl_data.loc[appl_data["model_category"] == job_category[0]]

        # print(type(link_list))

        names = names.values.tolist()
        for i in range(len(names)):
            for j in range(len(names[i])):
                # if 1<=j<=3:
                # temp_list = le.inverse_transform([names[i][j]])
                # names[i][j] = temp_list[0]
                names[i][j] = (j, names[i][j])
        print(names)

    # if names is None:
    #     names = "No applicant has been found"
    return render_template("recruiterout.html", output=names)
    """


# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('404.html'), 404


# Running the app
if __name__ == '__main__':

    try:
        applicants = pd.read_csv("assets/users.csv", header=0, index_col=False)
    except pd.errors.EmptyDataError as e:
        print(e)
        applicants = pd.DataFrame(columns=applicant_cols)

    app.run(host='0.0.0.0', port='5000', debug=True)
