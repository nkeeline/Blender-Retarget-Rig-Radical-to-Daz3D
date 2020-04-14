# Blender-Retarget-Rig-Radical-to-Daz3D Test

Tested and working on Blender 2.83

To execute the script run the script with the play button in blenders text editor. 

This is a simple python script to retarget a rig in blender from a radical capture to a rig imported from Daz3D.  It can be used to retarget any rig to any other below with some simple changes to the file detailed below:

The script applies the GLOBAL posiion and Rotations of a source rig to the destination rig.

To Modify for rigs other than a radical fbx import and a destination DAZ3d rig imported to blender do the following:

Just open the script in blender's text editer and edit these lines:

    SourceArmName = "Reference"
    DestArmName = "Leopold"
    KeyFrame_Every_Nth_Frame = 3
    NumberOfFramesToTransfer = 150
    
 If the names of the rig are different, put the name of your source armature in the SourceArmName variable etc.  For example... if the name of the source rig is "myimportedrig" change "Reference" above to "myimportedrig", likewise update the name of the destination rig in the same way...etc.

If you want to adapt the script to work with rigs with different named bones update the sction with lines like thie:

    SetBoneRotation(SourceArm, "LeftForeArm", DestArm, "lForearmBend", "lForearmTwist", NoCorrection, keyFrame, True)

update the name of the source arm (above it's "LeftForeArm") to the name of the forearm on the source rig.
update the name of the destination arm name.... shown as "lForearmBend" to the name of the destination bone on the destination rig you want the source bone to mapped to.  Do this for all bone mapping of rotation you wish to do.
if you don't have a twist bone, change the "lForearmTwist" to empty string, and change the last boolean input to the function above to False.  A twist bone is a special Genesis 8 bone that comes in from DAZ so set the bool to false if you're rig isn't from Daz) Leave the keyframe var and don't touch it, it's the scripts way of passing to the function whether a bone should be keyframed.

If after running the script the arm is twisted put a correction rotation in for the NoCorrection var in the function above(NoCorrection is a zero rotation unity quaternion that doesn't do anything, changing it to Correction_p90_Y_Quat will rotate the bone plus 90 degrees in the y after the mapping rotation is applied).  Exampes of available corrections are in the section of the script the start of which are shown below:

    NoCorrection = mathutils.Quaternion((1,0,0,0))
    Correction_p90_Y_Quat = mathutils.Euler((math.radians(0), math.radians(90.0), math.radians(0)), 'XYZ').to_quaternion()
    Correction_n90_Y_Quat = mathutils.Euler((math.radians(0), math.radians(-90.0), math.radians(0)), 'XYZ').to_quaternion()
    .....

Use any one of the provided corrections or copy and paste a row to create a new one.  figure out the correction to create by editting the bone to 'fix' it. If after a script is run, and if you have to twist it 90 in y, to fix it, use or create the appropriate one.

To modify how position is applied to the rig modify the below line:

    SetBonePosition(SourceArm, "Hips", DestArm, "hip", "", keyFrame)

this command modifies the root bone of both rigs.  Alternatively you can delete the line to not set the position of the destination rig to the source rig.
