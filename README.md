# Blender-Retarget-Rig-Radical-to-Daz3D Test

Tested and working on Blender 2.83

This is a simple python script to retarget a rig in blender from a radical capture to a rig imported from Daz3D.

Just open the script in blender's text editer and edit these lines:

SourceArmName = "Reference"
DestArmName = "Leopold"
KeyFrame_Every_Nth_Frame = 3
NumberOfFramesToTransfer = 150

fairly self explanatory by the names then run the script, put the name of your source armature in the SourceArmName variable etc.  If you want to adapt the script to work with rigs with different named bones update the sction with lines like thie:

    SetBoneRotation(SourceArm, "LeftForeArm", DestArm, "lForearmBend", "lForearmTwist", NoCorrection, keyFrame, True)

update the name of the source arm (above it's LeftForeArm) to the name fo the forearm on the source rig.
update the name of the destination arm name as "lForearmBend"
if you don't have a twist bone, change the "lForearmTwist" to empty string, any thing and change the last boolean input to the function above to false.
leave the keyframe var and don't touch it, it's the scripts way of passing to the function whether a bone should be keyframed.
if after running the script the arm is twisted put a correction rotation in the NoCorrection are.  Available correction are in the 

NoCorrection = mathutils.Quaternion((1,0,0,0))
Correction_p90_Y_Quat = mathutils.Euler((math.radians(0), math.radians(90.0), math.radians(0)), 'XYZ').to_quaternion()
Correction_n90_Y_Quat = mathutils.Euler((math.radians(0), math.radians(-90.0), math.radians(0)), 'XYZ').to_quaternion()
.....

Section, use one of the above corrections or copy and paste a row to create a new one.

