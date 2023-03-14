import csv
from scrapper import scrapper


def main():
    le_name_mapping = {0: 'Advocate', 1: 'Arts', 2: 'Automation Testing', 3: 'Blockchain', 4: 'Business Analyst',
                       5: 'Civil Engineer', 6: 'Data Science', 7: 'Database', 8: 'DevOps Engineer',
                       9: 'DotNet Developer', 10: 'ETL Developer', 11: 'Electrical Engineering', 12: 'HR', 13: 'Hadoop',
                       14: 'Health and fitness', 15: 'Java Developer', 16: 'Mechanical Engineer',
                       17: 'Network Security Engineer', 18: 'Operations Manager', 19: 'PMO', 20: 'Python Developer',
                       21: 'SAP Developer', 22: 'Sales', 23: 'Testing', 24: 'Web Designing'}
    for i in range(len(le_name_mapping)):
        links = scrapper(le_name_mapping[i], 'India')
        with open('links.csv', 'w') as l_object:
            l_writer = csv.writer(l_object)
            for j in range(len(links)):
                row = [le_name_mapping[i], links[j]]
                l_writer.writerow(row)
        l_object.close()
    print('Hello World')


if __name__ == '__main__':
    main()
