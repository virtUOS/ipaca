#nltk.download('punkt')
import nltk 
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker

spell = SpellChecker()
lemmatizer = WordNetLemmatizer()

#def analyze_solution(self, solution, word_snippets, error_types):
context = {}
analysis = {}

#snippets: It, are, funny, the, funniest, is, funnier, task
#User input: It is funnier task
right_answer = "This is the funniest task"

# tokenize: ["It", "is", "funnier", "task"]
tokenized_user_answer = nltk.word_tokenize(self.task.content)
print("user: " + tokenized_user_answer)
tokenized_right_answer = nltk.word_tokenize(right_answer)
print("solution: " + tokenized_user_answer)

#Spelling Correction

for word in tokenized_user_anwer:
    # if word is unknown, then it is not spelled correctly and hence will remain in the array
    if len(spell.unknown([word])) > 0:
        # replace the incorrect word with the `most likely` substitution
        word = spell.correction(word)


#lemmatize: 
lemmatized_user_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_user_answer]
lemmatized_right_answer = [lemmatizer.lemmatize(w.lower()) for w in tokenized_right_answer]

#check whether all words in the solution are also in the user solution
all_in = True
while all_in == True:
    for word in lemmatized_right_answer:
        if word not in lemmatized_user_answer:
            all_in = False


if self.task.content == given_answer:
    analysis['solved'] = True
else:
    analysis['solved'] = False

context['mode'] = "result"  # display to try again


    #It is the funniest task

#return (analysis, context)

