#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../src/'))
import rospy
from task_motion_planner.srv import *
from task_motion_planner.msg import *
from std_msgs.msg import *
from moveit_msgs.msg import *
from shape_msgs.msg import *
from geometry_msgs.msg import *
from sensor_msgs.msg import *
from pose_generator import *
from motion_plan_playback import *

#TODO: method to get the table center

CYLINDER_HEIGHT = 0.2
CYLINDER_RADIUS = 0.035

# make the state object for a world of with a given shape of cylinders (lines,cross,square,x)
def makeState(shape):
    state = world_state()
    state.world = world_obj()

    state.robot = robot()
    state.robot.id = 'left_arm'
    state.robot.state = RobotState()
    state.robot.state.joint_state.name = ['head_pan', 'left_e0', 'left_e1', 'left_s0', 'left_s1', 'left_w0', 'left_w1', 'left_w2', 'right_e0', 'right_e1', 'right_s0', 'right_s1', 'right_w0', 'right_w1', 'right_w2']
    state.robot.state.joint_state.position = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    state.robot.state.joint_state.velocity = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    state.robot.state.joint_state.effort = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # add surfaces
    state.world.surfaces.append(addSurf(state.world.surfaces,1,[1, 1, 0.05],[1,0,0]))
    # addSurf(state.world.surfaces,2,[1,.5,0.05],[0,.5,0])
    # add center cylinder
    addCylinder(state.world.movable_objects,0,getCenterCylinderPose(state.world.surfaces[0]))
    # center cylinder pose
    cylinder_pose = state.world.movable_objects[0].primitive_poses[0].position
    if(shape == 'VLINE'):
        # add above
        loc = [cylinder_pose.x + CYLINDER_RADIUS*3,cylinder_pose.y,cylinder_pose.z]
        addCylinder(state.world.movable_objects,1,loc)
        # add below
        loc = [cylinder_pose.x - CYLINDER_RADIUS*3,cylinder_pose.y,cylinder_pose.z]
        addCylinder(state.world.movable_objects,2,loc)
    elif(shape == 'HLINE'):
        # add left
        loc = [cylinder_pose.x,cylinder_pose.y - CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,1,loc)
        # add right
        loc = [cylinder_pose.x,cylinder_pose.y + CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,2,loc)
    elif(shape == 'CROSS'):
        # add above
        loc = [cylinder_pose.x + CYLINDER_RADIUS*3,cylinder_pose.y,cylinder_pose.z]
        addCylinder(state.world.movable_objects,1,loc)
        # add below
        loc = [cylinder_pose.x - CYLINDER_RADIUS*3,cylinder_pose.y,cylinder_pose.z]
        addCylinder(state.world.movable_objects,2,loc)
        # add left
        loc = [cylinder_pose.x,cylinder_pose.y - CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,3,loc)
        # add right
        loc = [cylinder_pose.x,cylinder_pose.y + CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,4,loc)
    elif(shape == 'SQUARE'):
        # add above
        loc = [cylinder_pose.x + CYLINDER_RADIUS*3,cylinder_pose.y,cylinder_pose.z]
        addCylinder(state.world.movable_objects,1,loc)
        # add below
        loc = [cylinder_pose.x - CYLINDER_RADIUS*3,cylinder_pose.y,cylinder_pose.z]
        addCylinder(state.world.movable_objects,2,loc)
        # add left
        loc = [cylinder_pose.x,cylinder_pose.y - CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,3,loc)
        # add right
        loc = [cylinder_pose.x,cylinder_pose.y + CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,4,loc)
        # add top left
        loc = [cylinder_pose.x + CYLINDER_RADIUS*3,cylinder_pose.y - CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,5,loc)
        # add top right
        loc = [cylinder_pose.x + CYLINDER_RADIUS*3,cylinder_pose.y + CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,6,loc)
        # add bottom left
        loc = [cylinder_pose.x - CYLINDER_RADIUS*3,cylinder_pose.y - CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,7,loc)
        # add right
        loc = [cylinder_pose.x - CYLINDER_RADIUS*3,cylinder_pose.y + CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,8,loc)
    elif(shape == 'X'):
        # add top left
        loc = [cylinder_pose.x + CYLINDER_RADIUS*3,cylinder_pose.y - CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,1,loc)
        # add top right
        loc = [cylinder_pose.x + CYLINDER_RADIUS*3,cylinder_pose.y + CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,2,loc)
        # add bottom left
        loc = [cylinder_pose.x - CYLINDER_RADIUS*3,cylinder_pose.y - CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,3,loc)
        # add right
        loc = [cylinder_pose.x - CYLINDER_RADIUS*3,cylinder_pose.y + CYLINDER_RADIUS*3,cylinder_pose.z]
        addCylinder(state.world.movable_objects,4,loc)
    return state

# add a surface object to the workd
def addSurf(surfaces,i,dim,position):
    # table surface 2
    surf = CollisionObject()
    surf.header = Header()
    surf.header.frame_id = '1'
    surf.id = 'surf' + str(i)
    primitive = SolidPrimitive()
    primitive.type = 1
    primitive.dimensions = dim
    surf.primitives.append(primitive)
    pose = Pose()
    pose.position.x = position[0]
    pose.position.y = position[1]
    pose.position.z = position[2]
    pose.orientation.w = 1
    surf.primitive_poses.append(pose)
    # surfaces.append(surf)
    return surf

# add a cylinder object to the world
def addCylinder(movable_objects,i,loc):
    obj = CollisionObject()
    obj.header = Header()
    obj.header.frame_id = '1'
    obj.id = 'obj' + str(i)
    primitive = SolidPrimitive()
    primitive.type = 3
    primitive.dimensions = [CYLINDER_HEIGHT, CYLINDER_RADIUS]
    obj.primitives.append(primitive)
    pose = Pose()
    pose.position.x = loc[0]
    pose.position.y = loc[1]
    pose.position.z = loc[2]
    pose.orientation.w = 1
    obj.primitive_poses.append(pose)
    movable_objects.append(obj)

# get the position of and object centered on the surface
def getCenterCylinderPose(surf):
    x = surf.primitive_poses[0].position.x
    y = surf.primitive_poses[0].position.y
    z = surf.primitive_poses[0].position.z + surf.primitives[0].dimensions[2]/2.0 + CYLINDER_HEIGHT/2.0
    return [x,y,z]

# get the height of cylinder resting on surface
def getCylinderHeight(surf):
    z = surf.primitive_poses[0].position.z + surf.primitives[0].dimensions[2]/2.0 + CYLINDER_HEIGHT/2.0
    return [x,y,z]

# test the wolr in the visualizer
def test(world_shape, action, motion_server, poseGen):
    state = makeState(world_shape)

    msg = motion_plan_parameters()
    msg.state = state
    msg.action = action
    msg.goals = poseGen.next(action, state)
    
    print msg.goals
    
    resp = motion_server(msg)
    
if __name__ == "__main__":
    rospy.wait_for_service('motion_server_service')
    motion_server = rospy.ServiceProxy('motion_server_service', motion_service)
    
    poseGen = PoseGenerator()
    
    # (pickup,obj1,left_arm,pose1,pose2)
    for i in range(1):
       test('X','(PICKUP,obj0,left_arm,pose1,pose2)', motion_server, poseGen)
    
    # (putdown,obj1,left_arm,pose1,pose2,tloc)
    # for i in range(5):
    #   test('VLINE','(PUTDOWN,obj0,left_arm,pose1,pose2,surf1)', motion_server, poseGen)