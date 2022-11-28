import json
import random

from .json5_template import template as TEMPLATE
from .json5_template import task as TASK
import json5
from pathlib import Path
from .nlp_models import NLP_Model
from textblob import TextBlob
from learning_environment.management.commands.read_lessons import Command
import copy


class AutomaticJson():
    nlp_model = NLP_Model()

    @staticmethod
    def stop_word_removal(noun_phrases):
        base = Path(__file__).parents[2]
        # Stop words were taken from www.countwordsfree.com
        path = '/learning_environment/utils/stop_words/stop_words_english.json'
        # stopwords =json.load('stop_words/stop_words_english.json')
        with open(str(base) + path) as j:
            stop_words = json.load(j)
            filtered_nouns = [w for w in noun_phrases if not w in stop_words]
            return filtered_nouns

    @staticmethod
    def noun_phrase_extraction(text):
        text = TextBlob(text)
        nouns_cleaned = AutomaticJson.stop_word_removal(text.noun_phrases)
        return nouns_cleaned

    @staticmethod
    def generate_q_a(text, number_questions=3):
        """
        Generates number_questions questions and answers and returns a list of tuples [(question,answer)... number_question]
        """
        AutomaticJson.text = text
        # extract noun phrases
        noun_phrases = [*set(AutomaticJson.noun_phrase_extraction(text))]

        number_questions = len(noun_phrases) if len(noun_phrases) < number_questions else number_questions

        clean_answers = random.sample(noun_phrases, k=number_questions)
        q_a = []

        for a in clean_answers:
            answer = a
            question = AutomaticJson.nlp_model.get_question(answer=answer, context=text)
            question = question.strip("<pad>").strip('</s>').strip(' question: ')

            q_a.append((question, a))
        return q_a

    @classmethod
    def create_json5(cls, data):
        """
        Creates a json5 representation of a lesson.
        data: dictionary that contains all the fields needed to create json5 representation of the lesson
        """

        template = copy.deepcopy(TEMPLATE)

        template['text'] = data['text']
        template['name'] = data['name']
        template['id'] = data['name'].lower().replace(' ', '_')

        template['text_source'] = data["text_source"]

        template['text_licence'] = data['text_licence']

        template['text_url'] = data['text_url']

        primary = True
        for q, a in data['tasks']:
            task = copy.deepcopy(TASK)
            task['question'] = q
            task['answer'] = a
            task['primary'] = primary
            template['tasks'].append(task)
            primary = False

        base = Path(__file__).parents[2]
        path = "/data/lessons/lesson_automatic_" + template['id'] + ".json5"
        filename = str(base) + path

        with open(filename, "w") as fp:
            json5.dump(template, fp,  indent=2)

        # saves automatic lessons to the database
        create_lesson = Command()
        create_lesson.handle(lesson_name="automatic_" + template['id'])
