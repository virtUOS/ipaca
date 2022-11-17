template = {
  'name': "Automatically Generated Task",  # the name that's also shown to the users
  'id': "xyznew",        # an internal id, will never be shown, but important to identify the lesson
  'series': 'Automatically Generated Task',
  'author': "User Me",    # used for documentation, will not be shown to the user
  'version': 1,                 # if you revise your lesson, give it a higher version number each time
  'text': "Lessons are the most fundamental building blocks of IPACA content.",
  'text_source': "some author of the text",
  'text_licence': "CC0",
  'text_url': "http:#www.virtuos.uos.de",
  'tasks': [  # the list of tasks for this lesson

  ],  # end of list of tasks
} # end of lesson

task = {  # task 1: primary reading task
  'name': "This is a name",
  'type': "R",  # Reading task - options: R = reading, GS = grammar/style, V = vocabulary
  'interaction': "SHORT",
  'primary': True,  # the primary task will be shown first, non-primary tasks are for repitition
  'show_lesson_text': True,  # Shall we show the lesson reading text? true/false
  'question': "",  # the question to be displayed
  'answer': ""
}  # end of task 1