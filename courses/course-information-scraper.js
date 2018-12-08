const fetch = require('node-fetch')
const fs = require('fs')
const Json2csvParser = require('json2csv').Parser
let parseString = require('xml2js').parseString

//  Call using raw data from link like:
//  https://courses.illinois.edu/cisapp/explorer/catalog/2019/spring.xml
const fetchRawXML = (url, format, callback) => {
  fetch(url).then((res) => {
    res.text().then((rawData) => {
      parseString(rawData, (err, result) => {
        format(result, callback)
      })
    })
  })
}

const formatSubjectList = (rawSubjectListData, callback) => {
  let subjects = []
  rawSubjectListData['ns2:term'].subjects[0].subject.forEach((subject) => {
    subjects.push({
      subject: subject['_'],
      code: subject['$'].id,
      link: subject['$'].href
   })
  })
  callback(subjects)
}

//  Call using raw data from link like:
//  https://courses.illinois.edu/cisapp/explorer/catalog/2019/spring/LAT.xml
const formatCourseList = (rawCourseList, callback) => {
  // console.log(rawSubjectData)
  let courses = []
  rawCourseList['ns2:subject']['courses'][0].course.forEach((course) => {
    courses.push({
      course_title: course['_'],
      course_number: course['$'].id,
      course_link: course['$'].href
    })
  })
  callback(courses)
}

//  Call using raw data from link like:
//  https://courses.illinois.edu/cisapp/explorer/catalog/2019/spring/LAT/580.xml
const formatCourse = (rawCourseData, callback) => {
  let course = rawCourseData['ns2:course']
  callback({
    course_fullname: course['$']['id'],
    course_description: course['description'][0],
    course_hours: course['creditHours'][0]
  })
}

function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

const URL_SUBJECTS = "https://courses.illinois.edu/cisapp/explorer/catalog/2019/spring.xml"
let SUBJECT_DROP = "subjects.csv"
let COURSE_DROP = "course-information.csv"


const cp_fields = ['department', 'department_code', 'course_title', 'course_number', 'course_description', 'course_hours']
const cp_opts = { cp_fields, header: false  }
const cp_parser = new Json2csvParser(cp_opts)

// const sp_field = ['subject','code','link']
// const sp_opts = { sp_field }
// const sp_parser = new Json2csvParser(sp_opts)


let NUM_WRITING = 0

fetchRawXML(URL_SUBJECTS, formatSubjectList, async (subjectList) => {
  let total_subjects = 0
  let total_courses = 0

  let num_subjects = 0
  for (let i = 0; i < subjectList.length; i++) {
    let subject = subjectList[i]
    let date = new Date().toString()
    console.log(date, "Made", subject.subject, "api call")

    fetchRawXML(subject.link, formatCourseList, async (courseList) => {
      let = rdate = new Date().toString()
      console.log(rdate, "Recieved", subject.subject, "data")
      let num_courses = 0
      for (let j = 0; j < courseList.length; j++) {
        let course = courseList[j]
        fetchRawXML(course.course_link, formatCourse, (course_info) => {
          total_courses += 1
          num_courses += 1
          let new_entry = {
            department: subject.subject,
            department_code: subject.code,
            course_title: course.course_title,
            course_number: course.course_number,
            course_description: course_info.course_description,
            course_hours: course_info.course_hours,
          }

          const csv = cp_parser.parse(new_entry);
          fs.appendFile(COURSE_DROP, csv + "\n", (err) => {})
        })
        await sleep(2500)
      }
    })
    await sleep(10000)
  }
})
