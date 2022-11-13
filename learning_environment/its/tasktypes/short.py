from learning_environment.its.base import Json5ParseException
#nltk.download('punkt')
import nltk 
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

class ShortTask():
    """A single choice task."""

    template = 'learning_environment/partials/short.html'

    @classmethod
    def check_json5(cls, task_json5, task_num=0):
        if "answer" not in task_json5:
            raise Json5ParseException(
                'Field "answer" is missing for short answer task task (task {})'.format(task_num))

    @classmethod
    def get_content_from_json5(cls, task_json5, task_num=0):
        return task_json5['answer']

    def __init__(self, task):
        self.task = task

    def analyze_solution(self, solution):
        context = {}
        analysis = {}

        #It is funnier task
        given_answer = solution.get('answer', None)

        # tokenize: ["It", "is", "funnier", "task"]
        tokenized_answer = nltk.word_tokenize(given_answer)

        #lemmatize: 
        lemmatized_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_answer]
        lemmatized_answer
        #It is the funniest task
         
        for word in given_answer if 

        if self.task.content == given_answer:
            analysis['solved'] = True
        else:
            analysis['solved'] = False

        context['mode'] = "result"  # display to try again
        return (analysis, context)

