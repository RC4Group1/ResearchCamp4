#!/usr/bin/python
import roslib
roslib.load_manifest('youbot_generic_states')
import rospy
import smach
import smach_ros
import tf
import arm_configuration
import brsu_srvs.srv
import std_srvs.srv

tf_listener = 0

class enable_object_finder(smach.State):

    def __init__(self):
        smach.State.__init__(
            self,
            outcomes=['succeeded', 'failed'])
        
        self.object_finder_srv_start = rospy.ServiceProxy('/youbot_object_finder/start', std_srvs.srv.Empty)

    def execute(self, userdata): 
        #get object pose list
        rospy.wait_for_service('/youbot_object_finder/start', 30)
        
        try:
            resp = self.object_finder_srv_start()
        except rospy.ServiceException, e:
            error_message = "%s"%e
            rospy.logerr("calling <</youbot_object_finder/start>> service not successfull, error: %s", error_message)
            return 'failed'
        
        return 'succeeded'

class detect_object(smach.State):

    def __init__(self):
        smach.State.__init__(
            self,
            outcomes=['succeeded', 'failed'],
            output_keys=['object_list'])
        
        self.object_finder_srv = rospy.ServiceProxy('/youbot_object_finder/GetObjectCandidates3D', brsu_srvs.srv.GetObjectCandidateList3D)
        self.object_finder_srv_stop = rospy.ServiceProxy('/youbot_object_finder/stop', std_srvs.srv.Empty)

        global tf_listener
        self.move_arm = arm_configuration.ArmConfiguration(tf_listener)

    def execute(self, userdata):     
        #get object pose list
        rospy.wait_for_service('/youbot_object_finder/GetObjectCandidates3D', 30)
        for i in range(20): 
            print "find object try: ", i
            resp = self.object_finder_srv()
              
            if (len(resp.pointCloudCentroids) <= 0):
                rospy.loginfo('found no objects')
                rospy.sleep(1);
            else:    
                rospy.loginfo('found {0} objects'.format(len(resp.pointCloudCentroids)))
                break
            
        #stop perception component
        rospy.wait_for_service('/youbot_object_finder/stop', 5)
        try:
            resp_stop = self.object_finder_srv_stop()
        except rospy.ServiceException, e:
            error_message = "%s"%e
            rospy.logerr("calling <</youbot_object_finder/stop>> service not successfull, error: %s", error_message)
            return 'failed'
    
        #move arm to home
        self.move_arm.moveToConfiguration("kinect_left_init")
        self.move_arm.moveToConfiguration("zeroposition")
    
        if (len(resp.pointCloudCentroids) <= 0):
            rospy.logerr("no graspable objects found");
            userdata.object_list = []            
            return 'failed'
        
        else:
            userdata.object_list = resp.pointCloudCentroids
            return 'succeeded'