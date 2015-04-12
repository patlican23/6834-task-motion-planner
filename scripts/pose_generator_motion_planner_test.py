#!/usr/bin/env python

import sys
import rospy
from task_motion_planner.srv import *
from task_motion_planner.msg import *
from pose_generator import *
from std_msgs.msg import *
from moveit_msgs.msg import *
from shape_msgs.msg import *
from geometry_msgs.msg import *
from sensor_msgs.msg import *

def pickupTest(action, motion_server, poseGen):
    state = world_state()
    state.world = PlanningSceneWorld()
    obj1 = CollisionObject()
    obj1.header = Header()
    obj1.header.frame_id = '1'
    obj1.id = 'obj1'
    primitive = SolidPrimitive()
    primitive.type = 3
    primitive.dimensions = [.1, .02]
    obj1.primitives.append(primitive)
    pose = Pose()
    pose.position.x = 0.5
    pose.position.y = 0
    pose.position.z = 0
    pose.orientation.w = 1
    obj1.primitive_poses.append(pose)
    state.world.collision_objects.append(obj1)

    state.robot = RobotState()
    state.robot.joint_state.name = ['head_pan', 'left_e0', 'left_e1', 'left_s0', 'left_s1', 'left_w0', 'left_w1', 'left_w2', 'right_e0', 'right_e1', 'right_s0', 'right_s1', 'right_w0', 'right_w1', 'right_w2']
    state.robot.joint_state.position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    state.robot.joint_state.velocity = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    state.robot.joint_state.effort = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    msg = motion_plan_parameters()
    msg.state = state
    msg.action = action
    msg.goals = poseGen.generate(action, state)
    
    print msg.goals
    
    resp = motion_server(msg)

def putdownTest():
    pass
    
if __name__ == "__main__":
    rospy.wait_for_service('motion_server_service')
    motion_server = rospy.ServiceProxy('motion_server_service', motion_service)
    
    poseGen = PoseGenerator()
    
    for i in range(10):
        pickupTest('(pickup,left_arm,obj1)', motion_server, poseGen)
