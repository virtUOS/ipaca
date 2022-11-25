from learning_environment.its.base import Json5ParseException
import nltk 
#nltk.download('punkt')
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
        self.beam_settings = TTSettings(num_beams=5, min_length=1, max_length=100)

    def analyze_solution(self, solution):
        context = {}
        analysis = {}

        #counts the errortpes
        errortypes = {'spelling': 0, 'grammar': 0, 'length': 0}

        
        


        #snippets: It, are, funny, the, funniest, is, funnier, task
        #User input: It is funnier task
        user_answer = solution.get('answer', None)

        # get the snippets to use
        word_snippets_str = self.task.question.replace(" ", "")
        word_snippets = word_snippets_str.split("/")
        
        print(word_snippets)

        #make sure it ends with a dot
        if not user_answer.endswith('.'):
            user_answer = user_answer +"."

    
        # tokenize: ["It", "is", "funnier", "task"]
        tokenized_user_answer = nltk.word_tokenize(user_answer)

        # gives the words's position in which the error type ocurrs
        # !starts at 0
        s_error = dict.fromkeys(tokenized_user_answer)

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
                s_error[tok_word] = 'spelling_error'

        #generate right answer with happy transformer
        right_answer = self.happy_tt.generate_text(user_answer, args=self.beam_settings).text
        print("corrected: ")
        print(right_answer)
        tokenized_right_answer = nltk.word_tokenize(right_answer)


        if(len(tokenized_user_answer) == len(tokenized_right_answer)):
            for i in range(len(tokenized_user_answer)):
                user_word = tokenized_user_answer[i]
                right_word = tokenized_right_answer[i]
                if right_word != user_word:
                        errortypes['grammar'] += 1
                        s_error[user_word] = 'grammar_error'
        
        else:
            errortypes['length'] += 1
        

        print(errortypes)
        print(s_error)



        
        #lemmatize: 
        lemmatized_user_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_user_answer]
        lemmatized_right_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_right_answer]
        print(lemmatized_right_answer)
        print(lemmatized_user_answer)
        #check whether all words in the solution are also in the user solution
        snippets_in = 0
        enough_words_used = True
        for word in word_snippets:
            if word in lemmatized_user_answer:
                snippets_in += 1
        if snippets_in < 3:
            enough_words_used = False

    
        print("enough words used? ")
        print(enough_words_used)
        
         
       #error_feedback = "You had " + errortypes['spelling'] +" spelling errors and " + errortypes['grammar'] +" gramar errors."
        if errortypes['spelling'] + errortypes['grammar'] == 0 :
            feedback = "Congratulations! There was no mistake."
            analysis['solved'] = True
        
        else:  
            #underlined_word = "\u0332".join(word + " ")
            feedback = "You had an error"
            analysis['solved'] = False
            context['mode'] = "result" 

        context['feedback'] = feedback # display to try again 

        corrected_user_underlined = ""
        for word in s_error:
            corrected_user_underlined += word + " "

        context['corrected_user_underlined'] = corrected_user_underlined        

        return (analysis, context)

