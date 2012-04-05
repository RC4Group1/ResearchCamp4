#!/usr/bin/python
import roslib
roslib.load_manifest('raw_generic_states')
import rospy
import smach
import smach_ros
import tf
import arm_configuration
import math

tf_listener = 0

class grasp_random_object(smach.State):

    def __init__(self):
        smach.State.__init__(
            self,
            outcomes=['succeeded', 'failed'],
            input_keys=['object_list'])
        
        global tf_listener
        self.move_arm = arm_configuration.ArmConfiguration(tf_listener)

    def execute(self, userdata):
        self.move_arm.moveGripperOpen()
        self.move_arm.moveToConfiguration("zeroposition")
        
        for object in userdata.object_list:         
            # ToDo: need to be adjusted to correct stuff           
            if object.z <= 0.18 and object.z >= 0.25:
                continue
            
            #target_pose = self.move_arm._createPose(object.x + 0.01, 0.0, object.z + 0.06, 0, math.pi, 0)

	    print "OOOOO1",object.y

	    if(object.y < 0.03):
		object.y = object.y - (object.y * 0.12)
	    elif(object.y > 0.03):
	    	object.y = object.y - (object.y * 0.15)

	    print "OOOOO2",object.y

	    #object.y = object.y - 0.02

            #target_pose = self.move_arm._createPose(object.x - 0.06, object.y - 0.02, object.z + 0.02, 0, ((math.pi/2) + (math.pi/4)), 0)
            target_pose = self.move_arm._createPose(object.x - 0.06, object.y, object.z + 0.06, 0, ((math.pi/2) + (math.pi/4)), 0)
            
            ik_result = self.move_arm.moveToPose(target_pose)
            
            if ik_result == True:
                self.move_arm.moveGripperClose()
                rospy.sleep(4.0)
                self.move_arm.moveToConfiguration("zeroposition")        
                return 'succeeded'    
            else:
                print 'could not find IK for current object'

        return 'failed'
        
        
        
        
        
    

class place_obj_on_rear_platform(smach.State):

    def __init__(self):
        smach.State.__init__(
            self,
            outcomes=['succeeded', 'failed'],
            input_keys=['rear_platform_free_poses', 'rear_platform_occupied_poses'],
            output_keys=['rear_platform_free_poses', 'rear_platform_occupied_poses'])
        
        global tf_listener
        self.move_arm = arm_configuration.ArmConfiguration(tf_listener)

    def execute(self, userdata):   
        
        self.move_arm.moveToConfiguration("zeroposition")
        self.move_arm.moveToConfiguration("pregrasp_back_init")
        self.move_arm.moveToConfiguration("pregrasp_back")
        
	if(userdata.rear_platform_free_poses > 0):
            pltf_pose = userdata.rear_platform_free_poses.pop()
	else:
	    pltf_pose = [0.033 + 0.024 - 0.32, 0.0, 0.12, 0, -math.pi + 0.2, 0];
        
        target_pose = self.move_arm._createPose(pltf_pose[0], pltf_pose[1], pltf_pose[2], pltf_pose[3], pltf_pose[4], pltf_pose[5], "arm_link_0")
        
        self.move_arm.moveToPose(target_pose)
        self.move_arm.moveGripperOpen()
        rospy.sleep(2.0)

        userdata.rear_platform_occupied_poses.append(pltf_pose)

	self.move_arm.moveToConfiguration("pregrasp_back")
        
        return 'succeeded'
    
    
class move_arm_out_of_view(smach.State):

    def __init__(self):
        smach.State.__init__(
            self,
            outcomes=['succeeded', 'failed'])
        
        global tf_listener
        self.move_arm = arm_configuration.ArmConfiguration(tf_listener)

    def execute(self, userdata):   
        self.move_arm.moveToConfiguration("zeroposition")  
        self.move_arm.moveToConfiguration("pregrasp_back_init")
        self.move_arm.moveToConfiguration("pregrasp_back")
        #self.move_arm.moveToConfiguration("kinect_left_init") 
        # self.move_arm.moveToConfiguration("kinect_left") 
           
        return 'succeeded'
    
    
