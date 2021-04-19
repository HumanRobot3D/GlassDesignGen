import bpy
import random
import math
import bmesh


class Options:

    #Scene Settings
    render_path = r'D:\GOOGLE_DRIVE\WORK\3D_Work\Generative_design\renders\11'
    end_frame = 360

    #Camera
    cam_zoom = 12 #smaller number means more zoomed in

    #Empty (these are mostly responsible for the rotation of arrays modifiers)
    empty_rot_divider = [3, 12] #this number will divide 360, essential for an array that goes full circle

    #Curves
    num_curves = [2, 5] 
    num_points = [4, 8] 
    points_loc_xy = [-5, 5] 
    points_loc_z = [0, 9] 
    cyclic_frequency = 0.2
    smooth_modif_iterations = 400 
    screw_modif_amount = [0.02, 0.2] #Control the width of the curves
    solidify_modif_thickness = [0.03, 0.2] 
    wave_modifier_presence = True
    wave_modif_height = [2, 8] 
    wave_modif_loop_length = [1, 2] #This divide end_frame, higher number means shorter animations
    wave_modif_width = [2, 10] #Don't go lower than 2, otherwise wave speed - which is derived from width - will get so low that they will get innacurate and fail looping.
    wave_modif_narrowness = [1, 5] #This is a divider, higher means less narrow
    random_remesh = True
    random_remesh_frequency = [0, 3] #Always 0 as minimum. TODO rework to be a value between 0 and 1 instead of a list
    remesh_modif_voxel_size = [0.06, 0.15]
    
    #Glass materials
    glass_roughness = [0.01, 0.3]

    #Random Z movements
    random_locz_frequency = [2, 4] #Number of Z positions blender will interpolate between. First and last frame (+ 1, for proper loop) are included but as the same position. So a frequency of 2 means that the objects will oscillate between 2 random position
    random_locz_intensity = 2 #This is a position multiplier, higher number means the movement will be more intense 

    #Random rotations
    random_rot_frequency = [0, 3] #TODO rework to be a value between 0 and 1 instead of a list
    random_rot_intensity = [1, 2] #Multiplier for the rotation amount based on empty inital rotation.

    #Sphere Solo
    sphere_presence = True
    sphere_frequency = .1 #How often the sphere solo will be added
    sphere_subdiv = [2, 5]
    sphere_size = [.5, 3] #This is a multiplier for the bmesh creation (so don't expect your usual blender scale values)

    #Spheres Array
    spheres_presence = True
    spheres_frequency = .1 #How often the spheres array will be added
    spheres_subdiv = [1, 4]
    spheres_size = [.1, .6] #This is a multiplier for the bmesh creation (so don't expect your usual blender scale values)

    #Point Light
    light_zloc = [3,6]
    light_intensity = 300

    min_light_zloc = 3
    max_light_zloc = 8

    center_cam = True

#Scene Settings
def sceneSettings():
    scene = bpy.context.scene

    #TODO This kinds of thing should be embeded in the UI
    scene.frame_end = Options.end_frame
    scene.render.engine = 'CYCLES'
    scene.render.use_motion_blur = True


#Delete all the data (objects, materials, meshes, images, etc)
def purgeAllData():

    D = bpy.data

    purge_list = [
        D.objects,
        D.materials,
        D.meshes,
        D.lights,
        D.curves,
        D.cameras,
        D.collections,
        D.worlds,
        D.images]
    
    for data_type in purge_list:
        for data in data_type:
            data_type.remove(data)

#Create Environment collection and add a Sun, Ground, and Camera.
def createEnvironment():
    scene = bpy.context.scene

    #Create an Environment collection for the 'environement' objects (Sun, Ground, Camera...)
    env_col = bpy.data.collections.new("Environment")
    scene.collection.children.link(env_col)

    #Create a Sun
    sun_data = bpy.data.lights.new(name = "Sun data", type = "SUN")
    sun_data.energy = 50
    sun_data.color = (0.358473, 0.420524, 0.592578)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    env_col.objects.link(sun_obj)
    sun_obj.location[0] = 4.83
    sun_obj.location[2] = 9.85
    sun_obj.rotation_euler[1] = math.radians(30)
    
    #Create a Ground
    ground_mesh = bpy.data.meshes.new("Ground mesh")
    verts = [(-20, -20, 0), (-20, 20, 0), (20, 20, 0), (20, -20, 0)]
    bm = bmesh.new()
    for v in verts:
        bm.verts.new(v)
    face = bm.faces.new(bm.verts)
    bmesh.utils.face_flip(face)
    bm.to_mesh(ground_mesh) 
    bm.free() #prevent further access

    ground_obj = bpy.data.objects.new("Ground", ground_mesh)
    env_col.objects.link(ground_obj) 
    ground_obj.location[2] = -10

    ground_mat = bpy.data.materials.new("Ground mat")
    ground_mat.use_nodes = True
    ground_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.208713, 0.208713, 0.208713, 1) #Color
    ground_mat.node_tree.nodes["Principled BSDF"].inputs[5].default_value = 0 #Roughness
    ground_mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value = 1 #Specularity
    ground_obj.data.materials.append(ground_mat)

    #Create a Camera
    cam_data = bpy.data.cameras.new("Cam data")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = Options.cam_zoom
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    env_col.objects.link(cam_obj) 
    cam_obj.location[1] = -16.24
    cam_obj.location[2] = 7 #is overwritten when animating camera but it's just nice to not leave it on the ground when debugging
    cam_obj.rotation_euler[0] = math.radians(90) #is overwritten when animating camera but it's just nice to not leave it on the ground when debugging
    bpy.ops.view3d.view_camera()

    #Create a World
    hdri_path = r'D:\GOOGLE_DRIVE\Ressources\Textures\HDRI\Studios\HDRI_STUDIO_vol2_052.png'

    world = bpy.data.worlds.new('World')
    scene.world = world
    world.use_nodes = True

    background = world.node_tree.nodes['Background']
    background.inputs['Strength'].default_value = 1.5
    background.location[0] = -300

    hdri_img = bpy.data.images.load(hdri_path)
    hdri_img.colorspace_settings.name = 'Non-Color'

    env_node = world.node_tree.nodes.new('ShaderNodeTexEnvironment')
    env_node.image = hdri_img
    env_node.location[0] = -700
    env_node.location[1] = 300

    world.node_tree.links.new(background.inputs['Color'], env_node.outputs['Color'])

    tex_coord = world.node_tree.nodes.new('ShaderNodeTexCoord')
    tex_coord.location[0] = -700
    tex_coord.location[1] = 0

    mapping = world.node_tree.nodes.new('ShaderNodeMapping')
    mapping.location[0] = -500
    mapping.location[1] = 0
    mapping.inputs[2].default_value[2] = -1.5708

    gradient = world.node_tree.nodes.new('ShaderNodeTexGradient')
    gradient.gradient_type = 'LINEAR'
    gradient.location[0] = -300
    gradient.location[1] = 0

    ramp = world.node_tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.00825129, 0.00825129, 0.00825129, 1)
    ramp.color_ramp.elements[1].color = (0.0217889, 0.0217889, 0.0217889, 1)
    ramp.location[0] = -100
    ramp.location[1] = 0

    world.node_tree.links.new(mapping.inputs['Vector'], tex_coord.outputs['Window'])
    world.node_tree.links.new(gradient.inputs['Vector'], mapping.outputs['Vector'])
    world.node_tree.links.new(ramp.inputs['Fac'], gradient.outputs['Color'])

    light_path = world.node_tree.nodes.new('ShaderNodeLightPath')
    light_path.location[0] = -700
    light_path.location[1] = 700

    mix = world.node_tree.nodes.new('ShaderNodeMixShader')
    mix.location[0] = 100
    mix.location[1] = 300

    world_output = world.node_tree.nodes['World Output']

    world.node_tree.links.new(mix.inputs['Fac'], light_path.outputs['Is Camera Ray'])
    world.node_tree.links.new(mix.inputs[1], background.outputs['Background'])
    world.node_tree.links.new(mix.inputs[2], ramp.outputs['Color'])
    world.node_tree.links.new(world_output.inputs['Surface'], mix.outputs['Shader'])

    return cam_obj

#Create a collection and make it active. Return the collection.
def createCollection(name):
    scene = bpy.context.scene

    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1] #Make the last created collection active
    return col

#Create an empty and randomize it's rotation. Return the empty.
def addRotatedEmpty(col):
    empty = bpy.data.objects.new("Empty", None)
    col.objects.link(empty)
    empty.rotation_euler[2] = math.radians(360/random.randint(Options.empty_rot_divider[0], Options.empty_rot_divider[1]))
    return empty

#Create a curve with a bunch of cool modifiers on it.
def addModifiedCurve(col, empty):
    scene = bpy.context.scene

    #Creating the curve
    curve_data = bpy.data.curves.new("Curve data", type = "CURVE")
    curve_data.dimensions = "3D"
    spline = curve_data.splines.new('BEZIER')

    num_points = random.randint(Options.num_points[0], Options.num_points[1])
    spline.bezier_points.add(num_points - 1) # -1 because 0 means 1 point is added.

    for point_num in range(num_points):
        point = spline.bezier_points[point_num]
        point.co = (
            random.uniform(Options.points_loc_xy[0], Options.points_loc_xy[1]), 
            random.uniform(Options.points_loc_xy[0], Options.points_loc_xy[1]), 
            random.uniform(Options.points_loc_z[0], Options.points_loc_z[1]))

        point.handle_right_type = 'AUTO'
    
    if random.uniform(0, 1) <= Options.cyclic_frequency:
        spline.use_cyclic_u = True

    curve_obj = bpy.data.objects.new("Curve", curve_data)
    col.objects.link(curve_obj)
            
    #Array Modifier
    array_modif = curve_obj.modifiers.new('Array', "ARRAY")
    array_modif.use_relative_offset = False
    array_modif.use_object_offset = True
    array_modif.offset_object = empty
    array_modif.count = 360/math.degrees(empty.rotation_euler[2]) + 1

    #Smooth Modifier
    smooth_modif = curve_obj.modifiers.new('Smooth', "SMOOTH")
    smooth_modif.use_apply_on_spline = True #TODO Is this useful/doing anything?
    smooth_modif.iterations = Options.smooth_modif_iterations

    #Screw Modifier
    screw_modif = curve_obj.modifiers.new('Screw', "SCREW")
    screw_modif.angle = random.uniform(Options.screw_modif_amount[0], Options.screw_modif_amount[1])

    #Solidify Modifier
    solidify_modif = curve_obj.modifiers.new('Solidify', "SOLIDIFY")
    solidify_modif.thickness = random.uniform(Options.solidify_modif_thickness[0], Options.solidify_modif_thickness[1])

    #Wave Modifier
    if Options.wave_modifier_presence == True:
        wave_modif = curve_obj.modifiers.new('Wave', "WAVE")
        wave_modif.width = random.uniform(Options.wave_modif_width[0], Options.wave_modif_width[1])
        wave_modif.height = random.uniform(Options.wave_modif_height[0], Options.wave_modif_height[1]) / wave_modif.width
        anim_length = scene.frame_end / random.choice(Options.wave_modif_loop_length)
        wave_modif.speed = (wave_modif.width * 2)/anim_length
        wave_modif.narrowness = wave_modif.height / random.uniform(Options.wave_modif_narrowness[0], Options.wave_modif_narrowness[1]) 
        wave_modif.time_offset = ((1/wave_modif.width)*anim_length)*-1
    
    #Remesh Modifier (applied randomly based on Options.random_remesh_frequency)
    if Options.random_remesh == True and random.choice(Options.random_remesh_frequency) == 0:       
        remesh_modif = curve_obj.modifiers.new('Remesh', "REMESH")
        remesh_modif.voxel_size = random.uniform(Options.remesh_modif_voxel_size[0], Options.remesh_modif_voxel_size[1])
        curve_obj.cycles.use_deform_motion = False #This need to be False so Motion blur doesn't get crazy trying to blur based on vertex position between each frame. Could be a cool effect with more persistent motion blur though? Probably not :D
    
    return curve_obj

#Create a random glass material and apply it to obj
def applyGlassMat(obj):
    mat = bpy.data.materials.new("Glass mat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[15].default_value = 1 #Transmission
    mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value = random.uniform(Options.glass_roughness[0], Options.glass_roughness[1]) #Roughness
    obj.data.materials.append(mat)

#Add random movements on the Z axis for all objects in obj_list. Movement will be synchronised for all objects in list.
def randomMovementZ(obj_list):
    scene = bpy.context.scene

    #First we need to figure out on which frame we want to keyframe movement. More keyframes = more frequent movement defined by Options.random_locz_frequency
    frequency = random.randint(Options.random_locz_frequency[0], Options.random_locz_frequency[1])
    frames_list = [1]
    for count in range(frequency-1):
        frames_list.append((scene.frame_end/frequency)*(count+1))
    frames_list.append(scene.frame_end+1)

    #Store object location on frame 1
    objects_locz = {}
    for obj in obj_list:
        objects_locz[obj] = obj.location[2] #Might look good to add a randomization on initial position too. Maybe. Gotta try it I guess at some point.

    #Iterate over frames_list and keyframe a random z location
    for frame in frames_list:
        rand_locz = (random.uniform(-1, 1) * Options.random_locz_intensity) / frequency #I divide by frequency so objects that moves faster moves less.
        for obj in obj_list:
            if frame == 1 or frame == (scene.frame_end + 1):
                obj.location[2] = objects_locz[obj]
            else: 
                obj.location[2] += rand_locz                     
            obj.keyframe_insert(data_path="location", frame = frame)

#Add a random rotation to objects. Unlike random position this is applied on only some objects, based on Options.random_rot_frequency
#Rotation can be based of a 'leading' object (needed for array modifiers), that will define rotation amount and will ensure animation is looping. If no object is provided the rotation will be randomized and looping.
def randomRotation(obj_list, leading_obj = None):
    scene = bpy.context.scene

    if random.choice(Options.random_rot_frequency) == 0:  
        frames_list = [1, scene.frame_end+1]

        if leading_obj == None:
            rotation_amount = 360/random.randint(Options.empty_rot_divider[0], Options.empty_rot_divider[1]) * random.randint(Options.random_rot_intensity[0], Options.random_rot_intensity[1])
        else:
            rotation_amount = math.degrees(leading_obj.rotation_euler[2]) * random.randint(Options.random_rot_intensity[0], Options.random_rot_intensity[1])

        #Iterate over frames_list and keyframe a rotation
        for frame in frames_list:
            for obj in obj_list:
                if frame == (scene.frame_end + 1):
                    if random.randint(0, 1) == 0:
                        obj.rotation_euler[2] += math.radians(rotation_amount)
                    else:
                        obj.rotation_euler[2] += math.radians(-rotation_amount)

                obj.keyframe_insert(data_path="rotation_euler", frame = frame)

#Add a solo sphere, with a random Z location and size, and possibly a scale on Z too.
def addSphereSolo(col):

    sphere_mesh = bpy.data.meshes.new("Sphere mesh")

    sphere_subdiv = random.randint(Options.sphere_subdiv[0], Options.sphere_subdiv[1])

    bm = bmesh.new()
    bmesh.ops.create_icosphere(
        bm, 
        subdivisions = sphere_subdiv, 
        diameter = random.uniform(Options.sphere_size[0], Options.sphere_size[1]))
    if sphere_subdiv >= 4:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(sphere_mesh) 
    bm.free() #prevent further access

    sphere_obj = bpy.data.objects.new("Sphere Solo", sphere_mesh)
    col.objects.link(sphere_obj)

    if random.randint(0,4) > 0:
        sphere_obj.scale[2] = 2

    return sphere_obj

#Add spheres in an array.
def addSpheresArray(col, empty):

    sphere_mesh = bpy.data.meshes.new("Spheres array mesh")

    spheres_subdiv = random.randint(Options.sphere_subdiv[0], Options.sphere_subdiv[1])

    bm = bmesh.new()
    bmesh.ops.create_icosphere(
        bm, 
        subdivisions = spheres_subdiv, 
        diameter = random.uniform(Options.spheres_size[0], Options.spheres_size[1]))
    if spheres_subdiv >= 3:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(sphere_mesh) 
    bm.free() #prevent further access

    spheres_obj = bpy.data.objects.new("Sphere array", sphere_mesh)
    col.objects.link(spheres_obj)

    #TODO find a non bpy.ops way to do this
    '''
    if random.randint(0,4) > 0:
        spheres_obj.scale[2] = 2
        bpy.context.view_layer.objects.active = spheres_obj
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    '''
        
    #Array Modifier
    array_modif = spheres_obj.modifiers.new('Array', "ARRAY")
    array_modif.use_relative_offset = False
    array_modif.use_object_offset = True
    array_modif.offset_object = empty
    array_modif.count = 360/math.degrees(empty.rotation_euler[2]) + 1

    return spheres_obj

#Add a point light in the middle of the sculpture
def addPointLight(col):
    scene = bpy.context.scene

    light_data = bpy.data.lights.new(name = "Point light data", type = "POINT")
    light_data.energy = Options.light_intensity
    light_data.color = (random.uniform(.5,1), random.uniform(.5,1), random.uniform(.5,1))
    light_obj = bpy.data.objects.new("Point Light", light_data)
    col.objects.link(light_obj)

    light_obj.location[2] = random.uniform(Options.light_zloc[0], Options.light_zloc[1])
    light_obj.keyframe_insert(data_path="location", frame = scene.frame_end)
    light_obj.location[2] = random.uniform(Options.light_zloc[0], Options.light_zloc[1])
    light_obj.keyframe_insert(data_path="location", frame = 1)

#Center camera on sculpture
def alignCamera(col, camera):
    scene = bpy.context.scene
    for current_frame in range(scene.frame_end):
        if current_frame%20 == 0 or current_frame == 1:

            #change frame
            scene.frame_set(current_frame)

            max_z_obj = []
            min_z_obj = []

            for obj in col.objects:
                if obj.type == "CURVE" or obj.type == 'MESH':

                    z_values = []

                    for point in range(0,7):
                        z_values.append(obj.bound_box[point][2] + obj.location[2])

                    max_z_obj.append(max(z_values))
                    min_z_obj.append(min(z_values))

            max_z_frame = max(max_z_obj)
            min_z_frame = min(min_z_obj)

            camera.location[2] = min_z_frame + (max_z_frame - min_z_frame)/2
            camera.keyframe_insert(data_path="location", frame = scene.frame_current)
                    
            print(str(scene.frame_current), str(max_z_frame), str(min_z_frame))

def compositing():
    scene = bpy.context.scene

    scene.use_nodes = True

    render_layers = scene.node_tree.nodes['Render Layers']
    render_layers.location[0] = -800

    scene.node_tree.nodes.new('ShaderNodeValToRGB')
class MY_OT_GenerateGlassDesign(bpy.types.Operator):
    bl_idname = "view3d.generateglassdesign"
    bl_label = "Generate glass design"
    bl_description = "Generate glass design"
    bl_options = {'REGISTER', 'UNDO'}

    test_mode: bpy.props.BoolProperty(name='Test mode (generate design but do not render)', default=True)
    render_number: bpy.props.IntProperty(name='Number of renders', default=1)
    animated: bpy.props.BoolProperty(name='Animated', default=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        scene = bpy.context.scene

        sceneSettings()
        
        #This loop based on the number of renders wanted
        for count in range(self.render_number):

            purgeAllData()
            camera = createEnvironment()
            col = createCollection("Procedural_Model")

            #This loop based on the number of curves (randomized)
            for count1 in range(random.randint(Options.num_curves[0], Options.num_curves[1])):
                
                empty = addRotatedEmpty(col)

                curve = addModifiedCurve(col, empty)

                applyGlassMat(curve)

                randomMovementZ(obj_list = [empty, curve])

                randomRotation(obj_list = [empty, curve], leading_obj = empty)

            for count2 in range(5):
                if Options.sphere_presence == True and random.uniform(0, 1) <= Options.sphere_frequency:
                    sphere_solo = addSphereSolo(col)
                    randomMovementZ(obj_list = [sphere_solo])
                    applyGlassMat(sphere_solo)
     
            for count3 in range(5):
                if Options.spheres_presence == True and random.uniform(0, 1) <= Options.spheres_frequency:
                    empty_spheres = addRotatedEmpty(col)
                    spheres_array = addSpheresArray(col, empty_spheres)
                    randomMovementZ(obj_list = [spheres_array])
                    randomRotation(obj_list = [empty_spheres, spheres_array], leading_obj = empty_spheres)
                    applyGlassMat(spheres_array)
  
            addPointLight(col)
         
            alignCamera(col, camera)

            #TODO
            '''
            compositing()
            '''
            
            #scene.render.filepath = render_path.replace('\\','/') + '/' + str(t) + '_'
            #bpy.ops.render.render(animation=True)

        self.report({'INFO'}, 'Done')
        return {'FINISHED'}