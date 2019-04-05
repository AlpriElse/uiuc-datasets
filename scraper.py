# %%
import requests

URL_SUBJECTS = "https://courses.illinois.edu/cisapp/explorer/catalog/2019/spring.xml"
res = requests.get(URL_SUBJECTS)
print(res.text)

# %%
from bs4 import BeautifulSoup
soup = BeautifulSoup(res.text, "xml")

subjects = {}
for subject in soup.findAll('subject'):
    name = subject.get_text()
    link = subject.get('href')
    abbrev = subject.get('id')
    subject = {
        "name":name,
        "link":link,
        "abbrev":abbrev
    }
    subjects[abbrev] = subject

# %%
from pymongo import MongoClient
MONGO_URL = "<YOUR MONGODB URL>"
client = MongoClient(MONGO_URL)

# %%
db = client['scraped-data-drop']
subject_collection = db['subject-data']


def add_subject_to_db(subject):
    subject_id = subject_collection.insert_one(subject).inserted_id
    # print(subject_id)

# %%
count = 0
departments = {}
coursesLinks = []
print(len(subjects))
for key in subjects:
    # if count == 10:
    #     break
    curr_subject = subjects[key]
    link = curr_subject['link']
    res = requests.get(link)
    subject_soup = BeautifulSoup(res.text)

    college_code = subject_soup.find('collegecode').get_text()
    department_code = subject_soup.find('departmentcode').get_text()
    name = subject_soup.find('unitname').get_text() # subject name
    website_link = subject_soup.find('websiteurl').get_text()
    abbrev = subject_soup.find('ns2:subject').get('id')

    subject = {
        'college_code': college_code,
        'department_code': department_code,
        'name': name,
        'link': website_link,
        'abbrev': abbrev
    }

    # add_subject_to_db(subject)

    for course in subject_soup.findAll('course'):
        coursesLinks.append(course.get('href'))
    count += 1

# %%

subject_collection = db['course-data']


def add_course_to_db(course):
    if (subject_collection.find_one({"department_code": course['department_code'], "number": course['number']}) is None):
        course_id = subject_collection.insert_one(course).inserted_id
        print(course_id)
    else:
        print("Duplicate",course['department_code'], course['number'])



# %%
print(len(coursesLinks))

# %%
count = 0

for i in range(7000, len(coursesLinks)):
    courseLink = coursesLinks[i]
    # if count == 1:
    #     break
    res = requests.get(courseLink)
    # print(courseLink)
    course_soup = BeautifulSoup(res.text)

    general_education = []
    for category in course_soup.find_all('category'):
        general_education.append(category.get('id'))

    terms_offered = []
    for terms in course_soup.find_all('course'):
        terms_offered.append(terms.get_text())

    # print(course_soup)
    subject = ""
    if course_soup.find('subject') != None:
        subject = course_soup.find('subject').get('id')
    name = ""
    if course_soup.find('label') != None:
        name = course_soup.find('label').get_text()
    description = "No description listed."
    if course_soup.find('description') != None:
        description = course_soup.find('description').get_text()
    credit_hours = "Credit hours not listed."
    if course_soup.find('credithours') != None:
        credit_hours = course_soup.find('credithours').get_text()
    number = 0
    if course_soup.find('ns2:course') != None:
        number = course_soup.find('ns2:course').get('id').split(' ')[1]
    course = {
        "department_code": subject,
        "name": name,
        "description": description,
        "credit_hours": credit_hours,
        "general_education": general_education,
        "terms_offered": terms_offered,
        "number": int(number)
    }
    # print(course)
    add_course_to_db(course)
    count += 1


# %%
xsubject_collection.find_one({"department_code": "AAS", "number":10}) is None










#
