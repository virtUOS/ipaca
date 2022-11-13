#from learning_environment.its.base import Json5ParseException
#nltk.download('punkt')
import nltk 
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
from happytransformer import  HappyTextToText

spell = SpellChecker()
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

    def analyze_solution(self, solution, word_snippets, error_types):
        context = {}
        analysis = {}

        #snippets: It, are, funny, the, funniest, is, funnier, task
        #User input: It is funnier task
        right_answer = solution.get('answer', None)
        user_answer = self.task.content

        # tokenize: ["It", "is", "funnier", "task"]
        tokenized_user_answer = nltk.word_tokenize(user_answer)
        tokenized_right_answer = nltk.word_tokenize(right_answer)
        
        #Spelling Correction
        for tok_word in tokenized_user_anwer:
            for s_word in user_answer:
                # if word is unknown, then it is not spelled correctly and hence will remain in the array
                if len(spell.unknown([word])) > 0:
                    # replace the incorrect word with the `most likely` substitution
                    corr_word = spell.correction(word)
                    user_answer = user_answer.replace(s_word, corr_word)


        # happytransformer(lemmatized user answer)
        ht_output = happy_tt.generate_text(tokenized_user_answer, args=beam_settings)

        #lemmatize: 
        lemmatized_user_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_user_answer]
        lemmatized_right_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_right_answer]

        #check whether all words in the solution are also in the user solution
        all_in = True
        while all_in == True:
            for word in lemmatized_right_answer:
                if word not in lemmatized_user_answer:
                    all_in = False

        

        # definiere wie ähnlich ht und right_answer sein müssen
        # vergleiche ht und right_answer genau 
        if ht != given_answer:
            analysis['solved'] = False
            context['mode'] = "result"  # display to try again
        else:
            analysis['solved'] = True

        


         #It is the funniest task

        return (analysis, context)

