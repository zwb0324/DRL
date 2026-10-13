import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from torchvision import transforms
def pdb2img(filename, img_fn=None):
    fp = open(filename, "r")
    contents = fp.readlines()[1:-1]
    coords = np.array([list(map(float,x.split()[6:8])) for x in contents])
    fp.close()

    fig, ax = plt.subplots()
    
    DPI = fig.get_dpi()
    fig.set_size_inches(500.0/float(DPI), 500.0/float(DPI))

    ax.scatter(coords[:,0], coords[:,1], c='blue', s=400)
    ax.scatter(coords[:,0], coords[:,1], c='green', s=200)
    ax.scatter(coords[:,0], coords[:,1], c='yellow', s=60)
    ax.scatter(coords[:,0], coords[:,1], c='red', s=10)
    ax.axis('off')
    ax.axis('equal')
    ax.set_xticks([])
    ax.set_yticks([])

    fig.canvas.draw()
    X = np.array(fig.canvas.renderer.buffer_rgba())
    # plt.close()
    # plt.show()
    im = Image.fromarray(X)
    transform = transforms.Compose([
        transforms.CenterCrop((380, 380)),
        transforms.Resize((224, 224))
    ])
    transform(im).show()
    # im.show()
    if img_fn is not None:
        im.save(img_fn)
        print("image saved to {}".format(img_fn))


    return im

pdb2img('pore.pdb')