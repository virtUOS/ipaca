import sys

from json5_template import template, task
import json5
import glob

# import models
from nlp_models import NLP_Model



def text_to_json5():

    # read in text
    # text = "this is an example text. Let's create a question out of this."
    text = "I just returned from the greatest summer vacation! It was so fantastic, I never wanted it to end. I spent eight days in Paris, France. My best friends, Henry and Steve, went with me. We had a beautiful hotel room in the Latin Quarter, and it wasn’t even expensive. We had a balcony with a wonderful view."

    # select sentence to generate question
    ## for now, we choose a random noun
    answer = 'Henry'

    # generate question(based on answer? Noun?)
    nlp_model = NLP_Model()

    question = nlp_model.get_question(answer=answer, context=text)
    question = question.strip("<pad>").strip('</s>')
    print(question)

    # sys.exit()

    # insert into template and safe as Json5


    template['text'] = text
    task['question'] = question
    task['answer'] = answer

    template['tasks'] = [task]

    import os

    from pathlib import Path

    base = Path(__file__).parents[2]
    filename = str(base) + "/data/lessons/lesson_test_nlp.json5"
    path = "./data/lessons"

    with open(filename, "w") as fp:
        json5.dump(template, fp)


def main():
    text_to_json5()


if __name__ == '__main__':

    print('start')

    main()
