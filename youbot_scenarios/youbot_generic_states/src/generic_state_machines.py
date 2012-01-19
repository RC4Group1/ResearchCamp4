#!/usr/bin/python
import roslib; roslib.load_manifest('youbot_generic_states')
import rospy

import smach
import smach_ros

from generic_perception_states import *
from generic_manipulation_states import *

class sm_grasp_random_object(smach.StateMachine):
    def __init__(self):    
        smach.StateMachine.__init__(self, 
            outcomes=['object_grasped', 'failed'])
        
        with self:
            smach.StateMachine.add('FIND_OBJECT', detect_object(),
                transitions={'succeeded':'GRASP_OBJECT',  
                             'failed':'failed'})
                
            smach.StateMachine.add('GRASP_OBJECT', grasp_random_object(),
                transitions={'succeeded':'object_grasped', 
                            'failed':'failed'})