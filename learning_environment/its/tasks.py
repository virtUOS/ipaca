
# all active task types
import learning_environment.its.tasktypes.sc as sc
import learning_environment.its.tasktypes.mc as mc
import learning_environment.its.tasktypes.gap as gap
import learning_environment.its.tasktypes.mark as mark

# short names of active task types and their classes
TASK_TYPES = {'SC': sc.SCTask,
              'MC': mc.MCTask,
              'GAP': gap.GapTask,
              'MARK': mark.MarkTask}


