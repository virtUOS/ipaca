"""
Wrap the details of and access to specialised classes for different task types.

This introduces a level of abstraction that allows new task types to be added very easily.
To add a task type, you only need to:

1. Add an import, a shortcut and a class reference in the _TASK_TYPES dictionary in this class.
2. Create a class providing all required methods (see examples in its/tasktypes)
3. Create a template and integrate it into task.tmpl

"""
# all active task types
import learning_environment.its.tasktypes.sc as sc
import learning_environment.its.tasktypes.mc as mc
import learning_environment.its.tasktypes.gap as gap
import learning_environment.its.tasktypes.mark as mark
import learning_environment.its.tasktypes.short as short
import learning_environment.its.tasktypes.sortpar as sortpar

# short names of active task types and their classes
_TASK_TYPES = {'SC': sc.SCTask,
              'MC': mc.MCTask,
              'GAP': gap.GapTask,
              'MARK': mark.MarkTask,
              'SHORT': short.ShortTask,
              'SORTPAR': sortpar.SortParTask}

class TaskTypeFactory:
    """Picks the proper class or creates or proper object for a given interaction type or database Task object."""
    @classmethod
    def shortcuts(cls):
        """Returns a list of all registered interaction type shortcuts. Used for validating json5 representations."""
        return _TASK_TYPES.keys()
    @classmethod
    def getClass(cls, interaction):
        """Returns the class fitting the interaction shortcut."""
        return _TASK_TYPES[interaction]
    @classmethod
    def getObject(cls, task):
        """Returns an object fitting the Task object's interaction type."""
        return _TASK_TYPES[task.interaction](task)


