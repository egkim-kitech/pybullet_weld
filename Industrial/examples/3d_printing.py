"""This example shows how to use the extruder class to print a 3D object

This example shows how to use the pybullet_industrial package to simulate a 3D printing process.
The example uses a Comau NJ290 six-axis robot with a 3D printing head.
The 3D printing head is used to print a large hollowed out box with rounded edges.
"""
import os

import numpy as np
import pybullet as p
import pybullet_data
import pybullet_industrial as pi


def build_circular_path(center, radius, min_angle, max_angle, step_num, height):
    """Function which builds a circular path

    Args:
        center (array): the center of the circle
        radius (float): the radius of the circle
        min_angle (float): minimum angle of the circle path
        max_angle (float): maximum angle of the circle path
        steps (int): the number of steps between min_angle and max_angle

    Returns:
        array: array of 3 dimensional path points
    """
    circular_path = np.zeros((3, step_num))
    circular_path[2, :] = height
    for j in range(step_num):
        path_angle = min_angle+j*(max_angle-min_angle)/step_num
        new_position = center + radius * \
            np.array([np.sin(path_angle), np.cos(path_angle)])
        circular_path[:2, j] = new_position
    return circular_path


if __name__ == "__main__":
    dirname = os.path.dirname(__file__)
    urdf_file1 = os.path.join(dirname,
                              'robot_descriptions', 'comau_nj290_robot.urdf')
    urdf_file2 = os.path.join(dirname,
                              'robot_descriptions', '3d_printing_head.urdf')

    physics_client = p.connect(p.GUI)
    p.setPhysicsEngineParameter(numSolverIterations=5000)

    fofa_path = os.path.join(dirname,
                             'Objects', 'FoFa', 'FoFa.urdf')
    p.loadURDF(fofa_path, [-4, 5, 0], useFixedBase=True, globalScaling=0.001)

    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.loadURDF("cube.urdf", [1.9, 0, 0.5], useFixedBase=True)

    start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    robot = pi.RobotBase(urdf_file1, [0, 0, 0], start_orientation)

    #plastic = pi.Plastic(0.03, [1, 0, 0, 1])

    extruder_properties = {'maximum distance': 0.5,
                           'opening angle': 0,
                           'material': pi.Plastic,
                           'number of rays': 1}
    extruder = pi.Extruder(
        urdf_file2, [1.9, 0, 1.2], start_orientation, extruder_properties)
    extruder.couple(robot, 'printing_coupling_frame')

    target_position = np.array([1.9, 0, 1.03])
    steps = 100
    test_path = pi.build_box_path(
        target_position, [0.5, 0.6], 0.1, [0, 0, 0, 1], steps)
    for i in range(20):
        extruder.set_tool_pose(*test_path.get_start_pose())
        for _ in range(50):
            p.stepSimulation()

    while True:
        test_path.draw()
        for positions, orientations, _ in test_path:
            extruder.set_tool_pose(
                positions, p.getQuaternionFromEuler([0, 0, 0]))
            position, orientation = extruder.get_tool_pose()
            particle = extruder.extrude()

            for _ in range(30):
                p.stepSimulation()
        test_path.translate([0, 0, 0.03])
