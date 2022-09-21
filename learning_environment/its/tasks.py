
# all active task types
import learning_environment.its.tasktypes.sc as sc
import learning_environment.its.tasktypes.mc as mc
import learning_environment.its.tasktypes.gap as gap

# short names of active task types and their classes
TASK_TYPES = {'SC': sc.SCTask,
              'MC': mc.MCTask,
              'GAP': gap.GapTask}

class Json5ParseException(Exception):
    pass

