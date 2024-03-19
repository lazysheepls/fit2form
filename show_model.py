import time
import pybullet as p
import pybullet_data

# initialize the GUI and others
p.connect(p.GUI)
p.resetDebugVisualizerCamera(3, 90, -30, [0.0, -0.0, -0.0])
p.setTimeStep(1 / 240.)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Load table and plane
p.loadURDF("evaluation_results/000240_gripper.urdf")

# p.setGravity(0, 0, -9.8)
p.setGravity(0, 0, 0)

while 1:
    p.stepSimulation()
    time.sleep(1./240)