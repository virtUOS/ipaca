# from learning_environment.models import Json5ParseException
import re

class GapTask():
    """A fill-in-the-gap task."""

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

    def analyze_solution(self, solution):
        analysis = {'solved': True, 'solution': {}}
        context = {'mode': 'result'}

        for i in range(len(self.task.content)):  # iterate over list of text parts and gaps
            if 'name' in self.task.content[i]:  # if it's a gap
                sol = solution.get('solution-{}-{}'.format(self.task.id, self.task.content[i]['name']), ['---'])
                analysis['solution'][self.task.content[i]['name']] = sol
                gap_solved = False
                if sol != '---':
                    for o in self.task.content[i]['options']:
                        if o['text'] == sol and o['correct']:
                            gap_solved = True
                            break
                self.task.content[i]['solved'] = gap_solved  # TODO: Find a proper solution, this is monkey patching...
                self.task.content[i]['solution'] = sol  # TODO: Find a proper solution, this is monkey patching...
                if not gap_solved:
                    analysis['solved'] = False

        return (analysis, context)


