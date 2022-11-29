import re
import nltk 
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
from happytransformer import HappyTextToText, TTSettings, HappyWordPrediction

from learning_environment.its.base import Json5ParseException

# 'en_core_web_sm' download mit: python -m spacy download en_core_web_sm
#neuer pip install command:
import spacy


# Definitions
sp = spacy.load('en_core_web_sm')
spell = SpellChecker()
lemmatizer = WordNetLemmatizer()

class GapTask():
    """A fill-in-the-gap task."""

    template = 'learning_environment/partials/smartgap.html'

    @classmethod
    def check_json5(cls, task_json5, task_num):
        if 'gaps' not in task_json5 or not isinstance(task_json5['gaps'], dict):
            raise Json5ParseException(
                'Field "gaps" is missing or is not a dictionary for gap task (task {})'.format(task_num))
        if 'mode' not in task_json5['gaps']:
            raise Json5ParseException(
                'Field "mode" is missing in "maps" dictionary for gap task (task {})'.format(task_num))
        if not task_json5['gaps']['mode'].lower() in ['select', 'fillin']:
            raise Json5ParseException(
                'Field "mode" must be "select" or "fillin" in "gaps" dictionary for gap task (task {})'.format(task_num))
        gaps = re.findall(r'(_[a-z0-9]+_)', task_json5['question'])
        if not gaps:  # no gaps at all
            raise Json5ParseException(
                'Question must contain gaps marked like _1_, _2_, ... or _place_, _time_ etc. for task {}'.format(task_num))
        if len(gaps) != len(set(gaps)):  # there are duplicate gaps
            raise Json5ParseException('There are duplicate gap names in task {}'.format(task_num))
        for gap in gaps:
            if gap not in task_json5['gaps']:
                raise Json5ParseException(
                    'Gap "{}" is defined in question but in gaps list for task {} '.format(gap, task_num))
            gap_options = task_json5['gaps'][gap]
            if not isinstance(gap_options, list):
                raise Json5ParseException(
                    'Gap "{}" does not have a list of options for task {}'.format(gap, task_num))
            gcount = 0
            for g in gap_options:
                gcount += 1
                for choice_field in [("text", str, "a string"), ("correct", bool, "True or False"),
                                     ("feedback", str, "a string")]:
                    if choice_field[0] not in g:
                        raise Json5ParseException(
                            'Field "{}" is missing for option {} of gap {} in task {} '.format(
                                choice_field[0], gcount, gap, task_num))
                    if not isinstance(g[choice_field[0]], choice_field[1]):
                        raise Json5ParseException(
                            'Field "{}" for option {} of gap {} in task {} has wrong type, it has to be {}'.format(
                                choice_field[0], gcount, gap, task_num, choice_field[2]))

    @classmethod
    def get_content_from_json5(cls, task, task_num=0):
        # content of a gap is a list of dictionaries
        # gap items have name, text, correct and feedback fields
        # text items only have a text field
        text_gap_list = []
        for el in re.split(r'(_[a-z0-9]+_)', task['question']):  # split question text into text and gap pieces
            if re.match(r'(_[a-z0-9]+_)', el):  # append dict from gaps for a gap
                gapdict = {'options': task['gaps'][el], 'name': el, 'mode': task['gaps']['mode'].lower()}
                text_gap_list.append(gapdict)
            else:
                text_gap_list.append({'text': el})
        return text_gap_list

    def __init__(self, task):
        self.task = task
        self.happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
        self.happy_wp = HappyWordPrediction()
        self.beam_settings = TTSettings(num_beams=5, min_length=1, max_length=100)

    # number of syllables check function
    
    def syllable_count(word): 
        '''
        Counts the number of syllables of a given word.
        
        source: https://stackoverflow.com/questions/46759492/syllable-count-in-python
        '''
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
        syl_count = GapTask.syllable_count(stem_adj)

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
                        feedback_rule = "Adjectives with one vowel and ending with one consonant are formed by doubling the last consonant and adding -er for comparatives and -est for superlatives, e.g. " + feedback_rule
                    else: # more than one vowel oder more than one consonant at end
                        feedback_rule = stem_adj + '-' + stem_adj + 'er-' + stem_adj + 'est'
                        feedback_rule = "Adjectives with one syllable, not ending with -e and with more than one vowel or ending with more than one consonant are formed by adding -er for comparatives and -est for superlatives, e.g. " + feedback_rule

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
        analysis = {'solved': True, 'solution': {}}
        context = {'mode': 'result'}
       
    
        for i in range(len(self.task.content)):  # iterate over list of text parts and gaps
            if 'name' in self.task.content[i]:  # if it's a gap
                sol = solution.get('solution-{}-{}'.format(self.task.id, self.task.content[i]['name']), ['---'])
                analysis['solution'][self.task.content[i]['name']] = sol
                gap_solved = False
                sentence_start = self.task.content[i-1]['text'].split('<br>')[1] if '<br>' in self.task.content[i-1]['text'] else self.task.content[i-1]['text']
                sentence_end = self.task.content[i+1]['text'].split('<br>')[0] if '<br>' in self.task.content[i+1]['text'] else self.task.content[i+1]['text']
                full_sentence = (sentence_start + sol + sentence_end).strip() #full sentence includes users gap choice
                print(full_sentence)

        errortypes = {'spelling': 0, 'grammar': 0, 'length': 0}
        tokenized_user_answer = nltk.word_tokenize(full_sentence)
        s_error = dict.fromkeys(tokenized_user_answer)
        print("Tokenized user answer: ")
        print(tokenized_user_answer)

        spelling_replacements= {}
        spelling_array= []
        #Spelling Correction
        user_answer_corr = full_sentence
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

        #generate right answer with happy transformer
        right_answer = self.happy_tt.generate_text(user_answer_corr, args=self.beam_settings).text
        print("right answer: ")
        print(right_answer)
        tokenized_right_answer = nltk.word_tokenize(right_answer)
        print("tokenized right answer: ")
        print(tokenized_right_answer)

        #search adjective
        user_adj_sen = sp(right_answer)
        adj_exists = False
        for i in range(len(tokenized_right_answer)):
            tag = spacy.explain(user_adj_sen[i].tag_)
            if(tag.split(",")[0] == "adjective"):
                adj_exists = True
                if len(spelling_replacements) > 0:
                    if s_error[spelling_replacements[tokenized_right_answer[i]]] is not None:
                        adj_feedback = GapTask.adj_to_rule(tokenized_right_answer[i])
                        context['adj_feedback'] = adj_feedback 
                else:
                    if s_error[tokenized_right_answer[i]] is not None:
                        adj_feedback = GapTask.adj_to_rule(tokenized_right_answer[i])
                        context['adj_feedback'] = adj_feedback 

        context['adj_exists_feedback'] = adj_exists       



        #lemmatize: 
        lemmatized_user_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_user_answer]
        lemmatized_right_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_right_answer]

        print("lem right answer: ")
        print(lemmatized_right_answer)
        print("lem_user: ")
        print(lemmatized_user_answer)

        adj_in_paranthese = []
        #check whether all words in the solution are also in the user solution
        for i in range(len(tokenized_user_answer)):
            if tokenized_user_answer[i] == "(":
                if len(tokenized_user_answer) >= i+2:
                    adj_in_paranthese.append(tokenized_user_answer[i+1])
        print("adj in par: ")
        print(adj_in_paranthese)

        adj_used = False
        for word in lemmatized_right_answer:
            for i in adj_in_paranthese:
                if word in adj_in_paranthese:
                    adj_used = True
        
        context['adj_used_feedback'] = adj_used 

    
        print("adj_used_feedback ")
        print(adj_used)

        if sol != '---':
            
            if sum(errortypes.values()) == 0 :
                for o in self.task.content[i]['options']:
                    o['feedback'] = "Congratulations! There was no mistake."
                    context['success_feedback'] = o['feedback']
                    analysis['solved'] = True
                    gap_solved = True

                    correct = True
                    analysis['correct'] = correct
                    context['correct'] = correct
                
            
            self.task.content[i]['solved'] = gap_solved  
            self.task.content[i]['solution'] = right_answer

            if not gap_solved:  
                analysis['solved'] = False
                context['mode'] = "result" 
                context['user_answer'] = full_sentence
                
                context['correct_feedback'] = "A correct solution would be '"+ right_answer + "'."

                correct = False
                analysis['correct'] = correct

        


        """
        if sol != '---':
            for o in self.task.content[i]['options']:
                o['text'] = right_answer
                if o['text'] == sol and o['correct']:
                    gap_solved = True
                    break
        self.task.content[i]['solved'] = gap_solved  # TODO: Find a proper solution, this is monkey patching...
        self.task.content[i]['solution'] = sol  # TODO: Find a proper solution, this is monkey patching...
        if not gap_solved:
            analysis['solved'] = False
        """
        return (analysis, context)


