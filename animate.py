from graphviz import Source
import pickle
import pydot
import os
import imageio
import pyglet
import shutil
from PIL import Image, ImageSequence
from pyglet.gl import *


def change_shape(block_path):
    edges = list()
    for i in range(len(block_path)):
        if i == len(block_path)-1:
            break
        else:
            edges.append([block_path[i], block_path[i+1]])
    filepath = './out_vis/cfg.dot'
    graphs = pydot.graph_from_dot_file(filepath)
    graph = graphs[0]
    change_lines = list()
    graph = Source.from_file(filepath)
    for edge in edges:
        for num_lin, lin in enumerate(str(graph).splitlines()):
            if ('->' in lin) and (edge[0] in lin) and (edge[1] in lin):
                change_lines.append(num_lin)

    sep_dot = str(graph).splitlines()
    num = 0
    for i in change_lines:
        num += 1
        bef = '\n'.join(sep_dot[:i])
        af = '\n'.join(sep_dot[i+1:])
        # print(bef + af)
        if '[' not in sep_dot[i]:
            new = sep_dot[i] + ' [color=red penwidth=3]'
        else:
            ind = sep_dot[i].index(']')
            new = sep_dot[i][:ind] + ' color=red penwidth=3]'
        now = bef + new + af
        graph = Source(now)
        graph.render(f'./out_vis/animcfg/cfg{num}', format='jpg', view=False)


def block_path(executed_path):
    with open('./out_vis/block_lines.pickle', 'rb') as handle:
        block_lines = pickle.load(handle)
    with open('./out_vis/End.pickle', 'rb') as handle:
        End = pickle.load(handle)

    block_path = []
    for i in executed_path:
        if i == 1:
            block_path.append('Start')
        elif i == 0:
            block_path.append(str(End))
        for block, line in block_lines.items():
            if i in line:
                if block_path[-1] == str(block):
                    pass
                else:
                    block_path.append(str(block))
    return block_path


def resize_gif():
    # Output (max) size
    size = 1000, 1000
    # Open source
    im = Image.open("executed_path.gif")
    # Get sequence iterator
    frames = ImageSequence.Iterator(im)
    # Wrap on-the-fly thumbnail generator
    def thumbnails(frames):
        for frame in frames:
            thumbnail = frame.copy()
            thumbnail.thumbnail(size, Image.ANTIALIAS)
            yield thumbnail
    frames = thumbnails(frames)
    # Save output
    om = next(frames) # Handle first frame separately
    om.info = im.info # Copy sequence info
    om.save("executed_path.gif", save_all=True, append_images=list(frames))


def animation_gen(executed_path):
    jpg_dir = './out_vis/animcfg'  
    for f in os.listdir(jpg_dir):
        os.remove(os.path.join(jpg_dir, f))

    blk_pth = block_path(executed_path)
    change_shape(blk_pth)
    images = []
    for file_name in sorted(os.listdir(jpg_dir)):
        if file_name.endswith('.jpg'):
            file_path = os.path.join(jpg_dir, file_name)
            images.append(imageio.imread(file_path))
    imageio.mimsave('./out_vis/executed_path.gif', images, duration=2)
    
    shutil.copyfile('./out_vis/executed_path.gif', './executed_path.gif')
    resize_gif()

    ag_file = "executed_path.gif"
    animation = pyglet.resource.animation(ag_file)
    sprite = pyglet.sprite.Sprite(animation)
    win = pyglet.window.Window(width=sprite.width, height=sprite.height)
    r,g,b,alpha = 0.5, 0.5, 0.8, 0.5
    pyglet.gl.glClearColor(r,g,b,alpha)
    @win.event
    def on_draw():
        win.clear()
        sprite.draw()

    pyglet.app.run()
