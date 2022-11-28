from learning_environment.its.base import Json5ParseException
import nltk 
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
from happytransformer import HappyTextToText, TTSettings



#TODO:
# Fehler von Thelen für Präsi wegbekommen
# kommentieren
# code aufräumen
# install dokument erstellen, vllt allg doku, requirements?
# alle grammar errors ausgeben (auch wenn nicht adjektiv)

#neuer pip install command:
import spacy

# Download mit: python -m spacy download en_core_web_sm
sp = spacy.load('en_core_web_sm')
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


    # number of syllables check function
    # source: https://stackoverflow.com/questions/46759492/syllable-count-in-python
    def syllable_count(word):
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count



    def adj_to_rule(grammar_error_adj):
        feedback_rule = 'no feedback rule was chosen'


        # 1. get the stem of the adjective
        stem_adj = lemmatizer.lemmatize(grammar_error_adj, "a")
        syl_count = ShortTask.syllable_count(stem_adj)

        # 2. test for exceptions good, bad, little, old, far, late, much/many
        if (stem_adj == 'good' or stem_adj == 'bad' or stem_adj == 'little' or stem_adj == 'old' or stem_adj == 'far' or stem_adj == 'late' or stem_adj == 'much' or stem_adj == 'many'):
            # exception 
            if (stem_adj == 'good'):
                feedback_rule = "good-better-the best"
            elif (stem_adj == 'bad'):
                feedback_rule = 'bad-worse-the worst'
            elif (stem_adj == 'little'):
                feedback_rule = 'little-less-the least'
            elif (stem_adj == 'old'):
                feedback_rule = 'old-older/elder-the oldest/the eldest'
            elif (stem_adj == 'far'):
                feedback_rule = 'far-further-the furthest'
            elif (stem_adj == 'late'):
                feedback_rule = 'late-later-last/the latest'
            elif (stem_adj == 'much'):
                feedback_rule = 'much/many-more-the most'
            elif (stem_adj == 'many'):
                feedback_rule = 'much/many-more-the most'

            feedback_rule = "The adjective " + stem_adj + " is an exception. It's forms are: " + feedback_rule

        else:

            # 3. number of syllables check
            if (syl_count == 1):
                # 4. one syllable
                if stem_adj.endswith('e'): # ends with e
                    feedback_rule = stem_adj + '-' + stem_adj + 'r-' + stem_adj + 'st'
                    feedback_rule = "Adjectives with one syllable and ending with -e are formed by adding -r for comparatives and -st for superlatives, e.g. " + feedback_rule
                else:
                    vowels = {'a','e','i','o','u'}
                    vow_count = 0
                    for v in vowels:
                        vow_count += stem_adj.count(v)
                    if (vow_count <= 1) and (stem_adj[-1] not in vowels) and (stem_adj[-2] in vowels): # one vowel and one consonant at end
                        feedback_rule = stem_adj + '-' + stem_adj + stem_adj[-1] + 'er-' + stem_adj + stem_adj[-1] + 'est'
                        feedback_rule = "Adjectives with one vowel and ending with one constant are formed by doubling the last constant and adding -er for comparatives and -est for superlatives, e.g. " + feedback_rule
                    else: # more than one vowel oder more than one consonant at end
                        feedback_rule = stem_adj + '-' + stem_adj + 'er-' + stem_adj + 'est'
                        feedback_rule = "Adjectives with one syllable, not ending with -e and with more than one vowel or ending with more than one constant are formed by adding -er for comparatives and -est for superlatives, e.g. " + feedback_rule

            elif (syl_count >= 2):
                # 5. two or more syllables
                if stem_adj.endswith('y'): # ends with y
                    feedback_rule = stem_adj + '-' + stem_adj.replace('y', 'i') + 'er-' + stem_adj.replace('y', 'i') + 'est'
                    feedback_rule = "Adjectives with more than one syllable and ending with -y are formed by replacing the y with an i and adding -er for comparatives and -est for superlatives, e.g. " + feedback_rule
                else:
                    feedback_rule = stem_adj + '-' + 'more ' + stem_adj + '-' + 'most ' + stem_adj 
                    feedback_rule = "Adjectives with more than one syllable and not ending with -y are formed by prepending 'more' for comparatives and 'most' for superlatives, e.g. " + feedback_rule
            else:
                print('Something went wrong. The word stem has less than one syllable.')


        return feedback_rule


    def analyze_solution(self, solution):
        context = {}
        analysis = {}

        #counts the errortpes
        errortypes = {'spelling': 0, 'grammar': 0, 'length': 0}
        spelling_replacements= {}


        #snippets: It, are, funny, the, funniest, is, funnier, task
        #User input: It is funnier task
        user_answer = solution.get('answer', None)
        print("User answer:")
        print(user_answer)

        # get the snippets to use
        word_snippets_str = self.task.question.replace(" ", "")
        word_snippets = word_snippets_str.split("/")
        
        print("snippets:")
        print(word_snippets)

        #make sure it ends with a dot
        if not user_answer.endswith('.'):
            user_answer = user_answer +"."

    
        # tokenize: ["It", "is", "funnier", "task"]
        tokenized_user_answer = nltk.word_tokenize(user_answer)
        print("Tokenized user answer: ")
        print(tokenized_user_answer)



        s_error = dict.fromkeys(tokenized_user_answer)
        spelling_array= []
        #Spelling Correction
        user_answer_corr = user_answer
        for i in range(len(tokenized_user_answer)):
            tok_word = tokenized_user_answer[i]
            # if word is unknown, then it is not spelled correctly and hence will remain in the array
            if len(spell.unknown([tok_word])) > 0:
                # replace the incorrect word with the `most likely` substitution
                corr_word = spell.correction(tok_word)
                tokenized_user_answer[i] = corr_word
                user_answer_corr = user_answer_corr.replace(tok_word, corr_word)
                spelling_replacements[corr_word] = tok_word
                print("replacements: ")
                print(spelling_replacements)
                print("user answer corr: ")
                print(user_answer_corr)
                spelling_array.append("You typed '" + tok_word + "' did you mean '" + corr_word + "'?")
                errortypes['spelling'] += 1
                s_error[tok_word] = 'spelling_error'
                spelling_correction_feedback = ' '.join(spelling_array)
                print("spelling correction feedback: ")
                print(spelling_correction_feedback)
                context ['spelling_correction_feedback'] = spelling_correction_feedback
        #if errortypes['spelling'] == 0:
        #   user_answer_corr = user_answer
        #  print("user answer corr im else: ")
        # print(user_answer_corr)

        print("user answer corr nach if- else: ")
        print(user_answer_corr)

        #generate right answer with happy transformer
        right_answer = self.happy_tt.generate_text(user_answer_corr, args=self.beam_settings).text
        print("right answer: ")
        print(right_answer)
        tokenized_right_answer = nltk.word_tokenize(right_answer)
        print("tokenized right answer: ")
        print(tokenized_right_answer)


        if(len(tokenized_user_answer) == len(tokenized_right_answer)):
            for i in range(len(tokenized_user_answer)):
                user_word = tokenized_user_answer[i]
                right_word = tokenized_right_answer[i]
                if right_word != user_word:
                        errortypes['grammar'] += 1
                        s_error[user_word] = 'grammar_error'
        
        elif(len(tokenized_user_answer) <= len(tokenized_right_answer)):
            errortypes['length'] += 1
            missing_word = []
            missing_comma = False
            for word in tokenized_right_answer:
                if word not in tokenized_user_answer:
                    if word != ",":
                        missing_word.append(word)
                    else: 
                        missing_comma = True
                        context['missing_comma_feedback'] = missing_comma
            if len(missing_word) >= 2:
                missing_words_str = " the words " 
                for i in range(len(missing_word)):
                    if i == 0:
                        missing_words_str += "'" + missing_word[i] + "'"
                    else:
                        missing_words_str += " and '" + missing_word[i] + "'"
                    
            elif(len(missing_word) > 0):
                missing_words_str = "the word '" + missing_word[0] + "'"
                missing_word_feedback = "It seems like you missed " + missing_words_str + "."
                context['missing_word_feedback'] = missing_word_feedback 
            

        else:
            errortypes['length'] += 1
            #TODO: Wrong additional words? 

        

        print(errortypes)
        print(s_error)


        user_adj_sen = sp(right_answer)
        adj_exists = False
        for i in range(len(tokenized_right_answer)):
            tag = spacy.explain(user_adj_sen[i].tag_)
            print(user_adj_sen[i])
            print(tag)
            if(tag.split(",")[0] == "adjective"):
                adj_exists = True
                if s_error[spelling_replacements[tokenized_right_answer[i]]] is not None:
                    adj_feedback = ShortTask.adj_to_rule(tokenized_right_answer[i])
                    context['adj_feedback'] = adj_feedback 
        context['adj_exists_feedback'] = adj_exists 



        
        #lemmatize: 
        lemmatized_user_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_user_answer]
        lemmatized_right_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_right_answer]

        print("lem right answer: ")
        print(lemmatized_right_answer)
        print("lem_user: ")
        print(lemmatized_user_answer)

        #check whether all words in the solution are also in the user solution
        snippets_in = 0
        enough_words_used = True
        for word in word_snippets:
            if word.lower() in lemmatized_user_answer:
                snippets_in += 1
        if snippets_in < 3:
            enough_words_used = False
            context['enough_snippets_feedback'] = enough_words_used 


    
        print("enough words used? ")
        print(enough_words_used)

        
         
       #error_feedback = "You had " + errortypes['spelling'] +" spelling errors and " + errortypes['grammar'] +" gramar errors."
        if sum(errortypes.values()) == 0 :
            success_feedback = "Congratulations! There was no mistake."
            context['success_feedback'] = success_feedback
            analysis['solved'] = True
        
        else:  
            #underlined_word = "\u0332".join(word + " ")
            #feedback = "You had an error"
            analysis['solved'] = False
            context['mode'] = "result" 
            context['user_answer'] = user_answer
            
            context['correct_feedback'] = "A correct solution would be '"+ right_answer + "'."



        #context['feedback'] = feedback # display to try again 
        
         
         
        

        

        return (analysis, context)

