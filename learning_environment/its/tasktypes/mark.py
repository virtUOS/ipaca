from learning_environment.its.base import Json5ParseException
import re
import json

class MarkTask():
    """A mark-the-word(s) task.

        JSON5 extra fields besides general task fields are:

        marktext: String with markers like #1#word, #2#another-word etc.
        markers: A dictionary with further information on the markers. Keys are strings with numbers corresponding to the markers above.#

        Example:
            marktext: "We #1#code in the #2#morning.",
            markers: {
                '1': { description: 'Find the verb' },
                '2': { description: 'Find the noun' },
            }
    """

    @classmethod
    def check_json5(cls, task_json5, task_num):
        """Check if json5 structure for a mark-the-word task is valid.

        """

        # do we have a proper marktext field
        if 'marktext' not in task_json5 or not isinstance(task_json5['marktext'], str):
            raise Json5ParseException(
                'Field "marktext" is missing or is not a string (task {})'.format(task_num))

        # do we have words to mark at all?
        if not re.search(r'#[1-9]#', task_json5['marktext']):
            raise Json5ParseException(
                "There's no word marked as correct (use #1#word to #9#... to mark them) in task {}".format(task_num))

        # do we have a proper markers dictionary?
        if 'markers' not in task_json5 or not isinstance(task_json5['markers'], dict):
            raise Json5ParseException(
                'Field "markers" is missing or is not a distionary (task {})'.format(task_num))

        # TODO: check if all subdictionaries are correct

        # do all markers in the text have an entry in the markers dictionary?
        markers_in_text=[]
        for mark in re.findall(r"(#([1-9])#)?(\w+)", task_json5['marktext']):
            if mark[1] != '':
                if mark[1] not in task_json5['markers']:
                    raise Json5ParseException(
                        'No description for marker {} in task {}'.format(mark[1], task_num))
                markers_in_text.append(mark[1])

        # are all entries in the markers dictionary used in the text?
        for mark in task_json5['markers'].keys():
            if mark not in markers_in_text:
                raise Json5ParseException('Marker {} in markers list but not defined in text in task {}'.format(mark, task_num))


    @classmethod
    def get_content_from_json5(cls, task, task_num=0):
        """Take a checked json5 structure and convert it into databse representation."""

        global __mark_cnt  # helper variable for counting words in the markertext

        def refcnt(mobj):
            """Helper function to be called by regex substitution, using a counter"""
            global __mark_cnt
            # each word in the HTML version of the text is wrapped in a span with additional info, e.g.
            # <span data-wordcnt='0'>We</span>
            span = "<span data-wordcnt='{}'>{}</span>".format(__mark_cnt, mobj[0])
            __mark_cnt += 1
            return span

        marktext_clean = re.sub(r'#[1-9]#', r'', task['marktext'])  # remove #1# etc. from text

        # wrap all words in spans and add their index as data-attribute
        __mark_cnt = 0  # reset counter
        marktext_html = re.sub(r"([\w-]+)", refcnt, marktext_clean)

        # create a dictionary of words to mark
        # key = mark group (1-9)
        # value = list of word indices for this group
        marks = {'1':[], '2':[], '3':[], '4':[], '5':[], '6':[], '7':[], '8':[], '9':[]}
        words = re.findall(r"(#([1-9])#)?([\w-]+)", task['marktext'])  # find all words potentially including marks
        for widx in range(len(words)):
            w = words[widx]
            # w is, according to regex: ('#1#' or '', the number or '', the word)
            if w[1] != '':  # we have marked word
                marks[w[1]].append(widx)  # store the mark group

        # prepare database structure (to be stored as json)
        content = {}
        content['marktext'] = task['marktext']  # the raw text
        content['marktext_clean'] = marktext_clean  # the text without markers
        content['marktext_html'] = marktext_html  # the text with HTML span wrappers for display
        content['marks'] = marks  # the words to be marked
        content['markers'] = task['markers']  # the markers dictionary
        return content

    def __init__(self, task):
        self.task = task

    def analyze_solution(self, solution):
        """Analyse a submitted solution, store results and create feedback messages."""

        analysis = {'solved': False, 'solution': {}}
        context = {'mode': 'result'}

        # either empty (nothing clicked) or a JSON dictionary with clicked word numbers, e.g.
        # { 1: [67, 123],   # for marker 1, words with index 67 and 123 were marked
        #   2: [],          # for marker 2, no ward was marked
        #   3: [5],         # for marker 3, word with index 5 was marked
        #   ...
        sol = solution.get('solution')

        # empty solution: nothing clicked at all
        if sol == '':
            context['mode'] = 'solve'
            context['msg'] = "You didn't mark any words, please try again."
            return analysis, context

        # parse json structure
        try:
            soldict = json.loads(sol)
        except ValueError as e:
            context['msg'] = "JSON parse error! {}".format(e)
            return analysis, context

        # check if it's a dict
        if not isinstance(soldict, dict):
            context['msg'] = "Illegal JSON: not a dict, {}".format(soldict)
            return analysis, context

        # if the dict is empty: things were clicked and de-clicked
        found = False
        for i in range(1, 10):
            if soldict[str(i)] != []:
                found = True
        if not found:
            context['mode'] = 'solve'
            context['msg'] = "You didn't mark any words, please try again."
            return analysis, context

        # analyse solution
        solved = True
        num_correct = 0
        num_additional = 0
        num_missed = 0
        num_total = 0
        feedback_text = self.task.content['marktext_html']
        for i in range(1, 10):  # check all 9 possible markers
            # compare list of words marked for that group
            chosen = set(soldict[str(i)])
            correct = set(self.task.content['marks'][str(i)])
            num_total += len(correct)
            if correct == chosen:  # if not identical
                num_correct += len(correct)
            else:
                solved = False
                num_missed += len(correct.difference(chosen))
                num_additional += len(chosen.difference(correct))
            # prepare html for showing correct/false messages in context
            for m in chosen:
                if m in correct:
                    feedback_char = '✓'
                else:
                    feedback_char = '✗'
                feedback_text = re.sub(r"<span data-wordcnt='{}'>([\w-]+)</span>".format(m),
                                       r"<span data-wordcnt='{}' class='mark{}'>\1</span>&nbsp;{}".format(m, i, feedback_char),
                                       feedback_text)

        analysis['solved'] = solved
        analysis['num_correct'] = num_correct
        analysis['num_total'] = num_total
        analysis['num_missed'] = num_missed
        analysis['num_additional'] = num_additional

        context['feedback_text'] = feedback_text
        context['num_correct'] = num_correct
        context['num_total'] = num_total
        context['num_missed'] = num_missed
        context['num_additional'] = num_additional

        return analysis, context


