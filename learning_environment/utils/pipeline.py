from .json5_template import template, task
import json5
from pathlib import Path
from .nlp_models import NLP_Model
from textblob import TextBlob


class AutomaticJson():
    nlp_model = NLP_Model()

    @staticmethod
    def noun_phrase_extraction(text):
        text = TextBlob(text)
        return text.noun_phrases

    @classmethod
    def text_to_json5(cls, text, answer=None):

        # read in text
        # text = "this is an example text. Let's create a question out of this."
        #text = "I just returned from the greatest summer vacation! It was so fantastic, I never wanted it to end. I spent eight days in Paris, France. My best friends, Henry and Steve, went with me. We had a beautiful hotel room in the Latin Quarter, and it wasn’t even expensive. We had a balcony with a wonderful view."

        AutomaticJson.text = text
        # select sentence to generate question
        ## for now, we choose a random noun
        answer = 'Skills'

        # generate question(based on answer? Noun?)
        # nlp_model = NLP_Model()

        question = AutomaticJson.nlp_model.get_question(answer=answer, context=text)
        question = question.strip("<pad>").strip('</s>')
        print(question)



        # insert into template and safe as Json5


        template['text'] = text
        task['question'] = question
        task['answer'] = answer

        template['tasks'] = [task]

        base = Path(__file__).parents[2]
        filename = str(base) + "/data/lessons/lesson_b_test_01_nlp.json5"


        with open(filename, "w") as fp:
            json5.dump(template, fp)

        print()



