import json
import random

from .json5_template import template as TEMPLATE
from .json5_template import task as TASK
import json5
from pathlib import Path
from .nlp_models import NLP_Model
from textblob import TextBlob
from learning_environment.management.commands.read_lessons import Command



class AutomaticJson():
    nlp_model = NLP_Model()

    @staticmethod
    def stop_word_removal(noun_phrases):
        base = Path(__file__).parents[2]
        # Stop words were taken from www.countwordsfree.com
        path = '/learning_environment/utils/stop_words/stop_words_english.json'
        #stopwords =json.load('stop_words/stop_words_english.json')
        with open(str(base)+path) as j:
            stop_words = json.load(j)
            filtered_nouns = [w for w in noun_phrases if not w in stop_words]
            return filtered_nouns

            print()


    @staticmethod
    def noun_phrase_extraction(text):

        text = TextBlob(text)
        nouns_cleaned= AutomaticJson.stop_word_removal(text.noun_phrases)
        return nouns_cleaned

    @classmethod
    def text_to_json5(cls, text,name, text_source,text_licence,text_url,answer=None, number_questions=10):
        template = TEMPLATE.copy()

        template['text'] = text
        template['name'] = name
        template['id'] = name.lower().replace(' ', '_')

        template['text_source'] = text_source

        template['text_licence'] = text_licence

        template['text_url'] = text_url

        AutomaticJson.text = text
        # extract noun phrases
        noun_phrases = [*set(AutomaticJson.noun_phrase_extraction(text))]

        # if len(noun_phrases) < number_questions:
        #     number_questions = len(noun_phrases)

        number_questions = len(noun_phrases) if len(noun_phrases) < number_questions else number_questions

        clean_answers = random.sample(noun_phrases, k=number_questions)


        for a in clean_answers:
            answer = a
            question = AutomaticJson.nlp_model.get_question(answer=answer, context=text)
            question = question.strip("<pad>").strip('</s>')

            # insert into template and safe as Json5
            task = TASK.copy()
            task['question'] = question
            task['answer'] = answer

            template['tasks'].append(task)


        base = Path(__file__).parents[2]
        path = "/data/lessons/lesson_automatic_"+name.lower().replace(" ", "_")+".json5"
        filename = str(base) + path

        with open(filename, "w") as fp:
            json5.dump(template, fp)
            print(template)

        create_lesson = Command()
        create_lesson.handle()






