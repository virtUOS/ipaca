"""
ipaca Tutor Model for adaptive pretest
"""

import random
import math #for exponential function
from learning_environment.models import Lesson, Task, ProfileSeriesLevel


class NoTaskAvailableError(Exception):
    pass


class Tutormodel:

    def __init__(self, learner):
        """Initializes the tutor model for a given learner.
        learner: User object"""
        self.learner = learner



    def evaluate_testlet(self, testlet):
        """Evaluate correctness of testlet items"""
        evaluation = [] #bool list that stores correctness of each item 
        #check each item of current testlet
        for item in testlet:
            #TODO: If answer to item is correct
            if ... == True:
                evaluation.append(True)
            else:
                evaluation.append(False)
        return evaluation
    


    def update_ability_estimate(self, current_ability, evaluation):
        """Estimate ability based on answer correctness"""
        change = 0.0 #stores the amount of change in ability value
        #check evaluation to calculate change
        for item in evaluation:
            #for correct item
            if item == True:
                change += 1/len(evaluation)
            #for incorrect item
            else:
                change -= 1/len(evaluation)
        #calculate new ability
        new_ability = current_ability + change
        return new_ability
    


    def select_next_testlet(self, testlet_options, ability):
        """Calculates information amount in all next testlet options for ability by using testlet's IIF
        + chooses the one with highest information as next testlet"""
        info_testlet_options = [] #stores information amount of each testlet option
        #TODO: Iterate over all possible next testlet options
        for option in testlet_options:
            #TODO: Get parameters from testlet
            a = ???
            b = ???
            c = ???
            #Get information amount by using the Item Information Function (= derivative of IRF)
            information_amount = -( (a*(c-1)*math.exp(a*(ability-b))) / ((math.exp(a*(ability-b))+1)**2) )
            info_testlet_options.append(information_amount)
        #Choose testlet with highest information amount as next testlet
        next_testlet = max(info_testlet_options)
        return next_testlet
    


    def adaptive_pretest(self, current_panel, max_stage=3):
        """Main algorithm of pretest for a panel (we need to repeat twice: (1) Vocab, (2)Grammar)
        current_panel = topic of current panel (e.g. Vocabulary, Grammar)"""
        
        #assume average ability
        current_ability = 0.0
        #declare start stage
        current_stage = 0
        #TODO (adjust): provide start testlet
        testlet = ???
        #TODO: let user submit testlet
        #TODO (adjust): When submit-button pressed: evaluate correctness of testlet 
        evaluation = self.evaluate_testlet(testlet)
        #adjust ability estimate
        new_ability = self.update_ability_estimate(current_ability, evaluation)
        #increase stage
        current_stage += 1

        #while termination condition (max stage reached) not met
        while current_stage < max_stage:
            #TODO (adjust): get next options
            testlet_options = [] #stores all lesson objects of new stage
            ???
            #select best next testlet
            testlet = self.select_next_testlet(testlet_options, new_ability)
            #TODO: Let user submit testlet
            #evaluate correctness of testlet
            evaluation = self.evaluate_testlet(testlet)
            #adjust ability estimate
            new_ability = self.update_ability_estimate(current_ability, evaluation)
            #increase stage
            current_stage += 1

        #return final ability estimate as test result
        return new_ability


