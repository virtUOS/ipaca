from learning_environment.its.base import Json5ParseException
import random

class SortParTask():
    """A sortable paragraph task.
    
    A sortable paragraph task needs to have one task specific field:

    paragraphs: [
        "This is the first paragraph.",
        "This is the second paragraph.",
        "This is the third paragraph"
    ],

    There is an optional parameter "order" that may be used if the required order if paragraphs is not total.

    By default, the paragraphs will be shown randomly shuffled and have to be sorted into exactly the order 
    given in the definition.

    By providing the "order" parameter, you underspecify the required order:

    order: "1<3, 2<3",  # read: First paragraph has to be before third, second has to be before third (but the exact order of first or second does not matter)
    
    or

    order: "1<2, 2<3",  # read: First before second, second before first - this is the default order that will be used if no order is specified
    
    Each paragrph receives a random id, so that the correct order cannot be determined by looking at the HTML page source code.

    The task's content is sotred in the database as a dictonary:

    self.content = {
        'order' = [(23, 42), (42, 9)],  # list of tuples (x,y) with element with id x has to be sorted in front of element with id y
        'paragraphs' = [
            {'id':23, 'paragraph': 'This is the first paragraph.'},
            {'id':42, 'paragraph': 'This is the second paragraph.'},
            {'id':9, 'paragraph': 'This is the third paragraph.'},
        ]
     }
    """

    template = 'learning_environment/partials/sortpar.html'
    additional_js = 'learning_environment/partials/sortpar.js'

    def __init__(self, task):
        self.task = task

    def analyze_solution(self, solution):
        """Check if a given solution is correct.

        Returns tuple: (analysis, correct) 
        
        with 
        analysis: dictionary with keys solved (was the task solved correct?) and solution (representation of solution provided for database storage),
        contect:  dictionary to be passed to the template, will containt mode:result (show evaluation) or mode:solve (display for solving again).
        """

        # solution is expected to be a comma delimited string of numerical paragraph ids
        solution = solution['solution']
        if not solution[0]=='[' or not solution[-1]==']':
            raise Exception("Invalid solution string! ({})".format(solution))
        solution = solution[1:-1]
        try:
            sol = [int(x) for x in solution.split(',')]  # sol is a list of strings
        except ValueError:
            # malformed soluton string, must not happen as it comes from our javascript code
            raise Exception("Invalid solution string! ({})".format(solution))
        
        # check if all pairs given in the task's order list are correctly ordered
        correct = True
        for (x,y) in self.task.content['order']:
            if sol.index(x) >= sol.index(y):
                correct = False
                break

        # constructand return  result tuple
        analysis = {'solved': correct, 'solution':sol }
        context = {'mode': 'result', 'solution': sol}
        
        return (analysis, context)


    @classmethod 
    def check_order_constraints(cls, order_constraints):
        """Checks if a string of order constraints is correct and returns the parsed result.
        Returns: List of tuples (x,y) meaning: xth element has to be before yth element.
        Order contraints: n<m,k<m,... | n,m,k are Integers.
        """

        # cons: list of contraints  ""..., ..., ...""
        # each constraint: "x<y"
        cons = [x.strip() for x in order_constraints.split(',')]
        
        constraints = [] # to be constructed as list of int tuples

        # example: "1<3,2<3" will be split and parsed into [(1,3), (2,3)]

        for con in cons:
            order = [x.strip() for x in con.split('<')]
            if len(order) != 2:
                raise Json5ParseException("Order constraint must have the form x < y (x and y being numbers), not {}".format(con))
            try:
                x = int(order[0])
                y = int(order[1])
                # TODO: check if numbers are in valid range
            except ValueError:
                raise Json5ParseException("Order constraint must have the form x < y (x and y being numbers), not {}".format(con))
            constraints.append((x, y))
        
        return constraints


    @classmethod
    def check_json5(cls, task_json5, task_num=0):
        """Check if json5 representation is valid."""
        
        if not 'paragraphs' in task_json5:
            raise Json5ParseException('Field "paragraphs" is missing for sort paragraph task (task {})'.format(task_num))
        if not isinstance(task_json5['paragraphs'], list):
            raise Json5ParseException('Value for field "paragraphs" has to be a list (task {})'.format(task_num))
        if len(task_json5['paragraphs']) < 2:
            raise Json5ParseException('Sort paragraphs task must have at least two paragraphs')
        if 'order' in task_json5:
            SortParTask.check_order_constraints(task_json5['order'])
        for e in task_json5['paragraphs']:
            if not isinstance(e, str):
                raise Json5ParseException('Elements in list for field "paragraphs" have to be strings (task {})'.format(task_num))

        return True


    @classmethod
    def get_content_from_json5(cls, task_json5, task_num=0):
        """Get a storable representation of task content from json5 representation."""

        val = { 'order':None, 'paragraphs':[] }
        
        # create a list of randomly shuffled ids that's as long as the list of paragraphs
        shuffled_numbers = list(range(len(task_json5['paragraphs'])))
        random.shuffle(shuffled_numbers)

        # add the random id coresponding to the paragraph position and the paragraph itself
        for i in range(len(task_json5['paragraphs'])):
            val['paragraphs'].append({'paragraph': task_json5['paragraphs'][i], 'id': shuffled_numbers[i]})

        # either check and store specified order or construct a full order
        if 'order' in task_json5 and task_json5['order']:
            val['order'] = [(shuffled_numbers[x-1], shuffled_numbers[y-1]) for x, y in SortParTask.check_order_constraints(task_json5['order'])]
        else:
            val['order'] = [(shuffled_numbers[x], shuffled_numbers[x+1]) for x in range(len(task_json5['paragraphs'])-1)]
        
        return val
