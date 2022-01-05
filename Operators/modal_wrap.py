
from bpy.ops import OBJECT_OT_bake as op

def callback(ret):
    print('Callback triggered: {} !!'.format(ret))


def modal_wrap(modal_func, callback):
    def wrap(self, context, event):
        ret, = retset = modal_func(self, context, event)
        if ret in {'CANCELLED'}: # my plugin emits the CANCELED event on finish - yours might do FINISH or FINISHED, you might have to look it up in the source code, __init__.py , there look at the modal() function for things like return {'FINISHED'} or function calls that return things alike.
            print(f"{self.bl_idname} returned {ret}")
            callback(ret)
        return retset
    return wrap
    
# op._modal_org = op.modal
op.modal = modal_wrap(op.modal, callback)

