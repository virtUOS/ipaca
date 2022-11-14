#from learning_environment.its.base import Json5ParseException
#nltk.download('punkt')
import nltk 
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
from happytransformer import HappyTextToText, TTSettings

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
        self.happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
        #self.happy_wp = HappyWordPrediction()
        self.beam_settings = TTSettings(num_beams=5, min_length=1, max_length=100)

    def analyze_solution(self, solution):
        context = {}
        analysis = {}
        word_snippets = ["It", "is", "funnier", "the", "funniest", "tree", "task"]
        
        #counts the errortpes
        errortypes = {'spelling': 0, 'grammar': 0, 'length': 0}

        # gives the words's position in which the error type ocurrs
        # !starts at 0
        s_error = {}



        #snippets: It, are, funny, the, funniest, is, funnier, task
        #User input: It is funnier task
        user_answer = solution.get('answer', None)

        if not user_answer.endswith('.'):
            user_answer = user_answer +"."


        print("user: "+ user_answer)
    
        # tokenize: ["It", "is", "funnier", "task"]
        tokenized_user_answer = nltk.word_tokenize(user_answer)

        
        #Spelling Correction
        for i in range(len(tokenized_user_answer)):
            tok_word = tokenized_user_answer[i]
            # if word is unknown, then it is not spelled correctly and hence will remain in the array
            if len(spell.unknown([tok_word])) > 0:
                # replace the incorrect word with the `most likely` substitution
                corr_word = spell.correction(tok_word)
                
                tokenized_user_answer[i] = corr_word
                user_answer = user_answer.replace(tok_word, corr_word)
                errortypes['spelling'] += 1
                s_error[i] = 'spelling_error'
                print("corrected_user_answer: " + user_answer)

        #generate right answer with happy transformer
        right_answer = self.happy_tt.generate_text(user_answer, args=self.beam_settings).text
        print("right: ")
        print(right_answer)
        tokenized_right_answer = nltk.word_tokenize(right_answer)
        print("tok_right: ")
        print(tokenized_right_answer)
        print("tok_user: ")
        print(tokenized_user_answer)


        if(len(tokenized_user_answer) == len(tokenized_right_answer)):
            for i in range(len(tokenized_user_answer)):
                user_word = tokenized_user_answer[i]
                right_word = tokenized_right_answer[i]
                if right_word != user_word:
                        errortypes['grammar'] += 1
                        s_error[i] = 'grammar_error'
        
        else:
            errortypes['length'] += 1
        

        print(errortypes)
        print(s_error)



        """
        #lemmatize: 
        lemmatized_user_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_user_answer]
        lemmatized_right_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_right_answer]

        print("lem_user: ")
        print(lemmatized_user_answer)
        print("lem_right: ")
        print(lemmatized_right_answer)

        #check whether all words in the solution are also in the user solution
        all_in = True
        while all_in == True:
            for word in lemmatized_right_answer:
                if word not in lemmatized_user_answer:
                    all_in = False
        
        print("all_in: ")
        print(all_in)

        """
        
         
       #error_feedback = "You had " + errortypes['spelling'] +" spelling errors and " + errortypes['grammar'] +" gramar errors."
        if sum(errortypes.values()) == 0 :
            feedback = "Congratulations! There was no mistake."
            analysis['solved'] = True
        
        else:
            feedback = ""  
            for errortype in s_error:
                if errortype > 0:
                    feedback = "You had an error"
                    analysis['solved'] = False
                    context['mode'] = "result" 
        
        context['feedback'] = feedback # display to try again 
                


         #It is the funniest task

        return (analysis, context)

