import bpy
import gpu
import bgl
import os
import blf
from gpu_extras.batch import batch_for_shader

vertex_shader = '''

    uniform mat4 ModelViewProjectionMatrix;

    in vec2 texCoord;
    in vec2 pos;
    out vec2 texCoord_interp;

    void main()
    {
    gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f);
    gl_Position.z = 1.0;
    texCoord_interp = texCoord;
    }

    '''
fragment_shader = '''
    in vec2 texCoord_interp;
    out vec4 fragColor;
    
    uniform sampler2D image;


    void main()
    {
    fragColor = pow(texture(image, texCoord_interp), vec4(0.45f));
    }

'''

class Help_Draw():

    def __init__(self,context):
        self.context = context

    def add_handle(self):
        self.handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_image,(),'WINDOW', 'POST_PIXEL')  
       
    def remove_handle(self):
        if self.handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW') 
            self.handle = None   

    def update(self,x,y,width,height):        
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        global vertex_shader
        global fragment_shader

        self.shader = gpu.types.GPUShader(vertex_shader, fragment_shader)

   
        self.batch = batch_for_shader(
            self.shader, 'TRI_FAN',
            {  
                "pos":  ((self.x, self.y),(self.width, self.y),(self.width, self.height),(self.x,self.height)),
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            },
        )
    
    def set_image(self, img_name):
        script_file = os.path.realpath(__file__)
        script_dir = os.path.dirname(script_file)
        
        rel_filepath = bpy.path.abspath(script_dir+"//img/"+img_name)
        try:
            self.image = bpy.data.images.load(rel_filepath, check_existing=True)   
            self.image.gl_load()
            return self.image
        except:
            pass

    def get_image(self):
        return self.image
        

    def draw_text(self,text):
        font_id = 0
        blf.position(font_id, self.x, self.y, 0)
        blf.size(font_id, 50, 72)
        blf.draw(font_id, text)
  
    def draw_image(self):
        bgl.glEnable(bgl.GL_BLEND)
        if self.image is not None:
            try:
                bgl.glActiveTexture(bgl.GL_TEXTURE0)
                bgl.glBindTexture(bgl.GL_TEXTURE_2D,self.image.bindcode)

                self.shader.bind()
                self.shader.uniform_int("image", 0)
                self.batch.draw(self.shader) 
                return True
            except:
                pass
        bgl.glDisable(bgl.GL_BLEND)
        return False    


class Help_Operator(bpy.types.Operator):
    bl_idname = "scene.help"
    bl_label = "Help"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER"}

    image_path = "help_overlay_texture_tools.png"
    help_draw = None

    @classmethod
    def poll(cls, context):
        return True
        

    def execute(self, context):
        help_clicked = bpy.context.scene.help_tex_tools
        self.help_draw = self.__class__.help_draw

        if self.help_draw is None:    
            self.help_draw = Help_Draw(context)
            self.__class__.help_draw = self.help_draw

        if help_clicked:    
            self.help_draw.set_image(self.image_path)
            self.help_draw.add_handle()
            self.draw_image(50)
        else:
            self.help_draw.remove_handle()
    
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            try:
                context.area.tag_redraw()
                self.draw_image(50)
            except:
                pass

        return {'PASS_THROUGH'}

    def draw_image(self,y_offset):
        # positioning
        try:
            view = [area for area in bpy.context.screen.areas if area.type == 'VIEW_3D'][0]
            region = [region for region in bpy.context.area.regions if region.type =="UI"][0]

            image = self.help_draw.get_image()
            if image is not None:
                x = view.width-(region.width+image.size[0])
                y = view.height-(image.size[1] + y_offset)

                self.help_draw.update(x,y,x+image.size[0],y+image.size[1])
        
        except:
             pass


