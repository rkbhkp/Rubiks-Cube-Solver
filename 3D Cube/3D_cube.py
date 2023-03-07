from ursina import *
from itertools import product

app = Ursina()
headerText = Text(text = 'Use Keys to Rotate the Cube', origin = (0,0), color=color.black, scale = 2, position = (0,0.4))
dirText = Text(text = "KEYS:" + '\n' +
                      "\'U\': Rotate upper level" + '\n' + 
                      "\'D\': Rotate lower level" + '\n' + 
                      "\'L\': Rotate left level" + '\n' + 
                      "\'R\': Rotate right level" + '\n' + 
                      "\'F\': Rotate front level" + '\n' + 
                      "\'B\': Rotate back level" + '\n' + 
                      "\'E\': Rotate front middle level" + '\n' + 
                      "\'M\': Rotate front vertical middle level" + '\n' +
                      "\'S\': Rotate side vertical middle level" + '\n' +
                      "SHIFT + Key: Rotate in opposite direction", origin = (0,0), color=color.black, scale = 1.2, x=-0.45, y= -0.3)


skybox_image = load_texture('textures/sky0')
Sky(texture=skybox_image)

# Relate individual cube positions to the center cube
def parent_child_relationship(axis, layer):
  for w in vortex:
    w.position, w.rotation = round(w.world_position,1), w.world_rotation
    w.parent = scene
  
  center.rotation = 0
  
  for w in vortex:
    if eval(f'w.position.{axis}') == layer:
      w.parent = center

# Enable Keyboard Input
def input(key):
  if key not in rot_dict: return
  axis, layer, storage = rot_dict[key]
  parent_child_relationship(axis, layer)
  shift = held_keys['shift']
  eval(f'center.animate_rotation_{axis} ({-storage if shift else storage}, duration = 0.5)')

# Create Game Window
window.borderless = False
window.size = (800,800)
window.position = (2000, 200)
EditorCamera()

# Position Cube
center = Entity()

# Input Key Dictionary
rot_dict = {'u': ['y', 1, 90],    'e': ['y', 0, -90],    'd': ['y', -1, -90],
            'l': ['x', -1, -90],  'm': ['x', 0, -90],    'r': ['x', 1, 90],
            'f': ['z', -1, 90],   's': ['z', 0, 90],     'b': ['z', 1, -90]}

# Create Cube
vortex = []
for pos in product((-1,0,1), repeat=3):
  vortex.append(Entity(model='models/custom_cube', texture = 'textures/rubik_texture', position=pos, scale=1))

app.run()