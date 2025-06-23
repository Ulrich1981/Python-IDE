import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageTk

def capture_plot():
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = Image.open(buf)
    return ImageTk.PhotoImage(image)
