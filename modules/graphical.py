from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import warnings
import os
import matplotlib.cbook
from modules.utils import percentage

try:
    import tkinter as tk
except ModuleNotFoundError:
    print("TKINTER MODULE NOT FOUND. Suggest: install package python3-pil.imagetk")

warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

wait_popup = None
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
X_IMAGE = 400
MAX_HEIGHT = 400
BACKGROUND_COLOR = "#313445"
TEXT_COLOR = "#FFFFFF"
GREEN = '#00796b'
RED = '#d32f2f'
DEFAULT_CHART = "./settings/default_chart_1.png"
default_chart = None
RESET_MESSAGE = "UNABLE TO SHOW THE RESULTS.\nMVSO DOESN'T CONTAIN NONE OF THE TAGS INSERTED."


def init_colors():
    global COLORS
    COLORS = list(plt.get_cmap('Dark2')(np.arange(8)))
    COLORS += list(plt.get_cmap('tab20')(np.arange(20)))


def limit_text(text, length=None):
    return text[:length - 3] + '...' if length is not None and len(text) > length else text


def resize_image(img, width=None, height=None):
    if width is None and height is not None:
        hpercent = (height / float(img.size[1]))
        width = int((float(img.size[0]) * float(hpercent)))
    elif width is not None and height is None:
        wpercent = (width / float(img.size[0]))
        height = int((float(img.size[1]) * float(wpercent)))
    return img.resize((width, height), Image.ANTIALIAS)


def photo_image_open(image_path, width=None, height=None, max_width=None, max_height=None):
    return ImageTk.PhotoImage(image_open(image_path, width, height, max_width, max_height))


def image_open(image_path, width=None, height=None, max_width=None, max_height=None):
    img = Image.open(image_path)
    if width is not None or height is not None:
        img = resize_image(img, width, height)
    if max_width is not None and img.size[0] > max_width:
        img = resize_image(img, width=max_width)
    if max_height is not None and img.size[1] > max_height:
        img = resize_image(img, height=max_height)
    return img


def update_img(panel, path):
    img = photo_image_open(path, width=X_IMAGE, max_height=MAX_HEIGHT)
    panel.configure(image=img, background="white")
    panel.image = img


def init_full_window(iterative=True, title_1="", title_2="", title_3=""):
    window = tk.Tk()
    window.withdraw()
    window.resizable(False, False)
    top = tk.Frame(window, background=BACKGROUND_COLOR)
    top.pack(side="top")
    left = tk.Frame(top, background=BACKGROUND_COLOR)
    left.pack(side="left")
    right = tk.Frame(top, background=BACKGROUND_COLOR)
    right.pack(side="right")
    bottom = tk.Frame(window)
    bottom.pack(side="bottom")
    panel_image = tk.Label(left, image=None)
    panel_image.pack(side=tk.TOP, fill="both", expand="no", padx=(20, 0))

    p_text_1_title = tk.Label(left, text=title_1, background=BACKGROUND_COLOR, wraplength=X_IMAGE - 20,
                              fg=TEXT_COLOR, font="Helvetica 20 bold")
    p_text_1 = tk.Label(left, text=None, background=BACKGROUND_COLOR, wraplength=X_IMAGE - 20, fg=TEXT_COLOR)
    p_text_2_title = tk.Label(left, text=title_2, background=BACKGROUND_COLOR, wraplength=X_IMAGE - 20,
                              fg=TEXT_COLOR, font="Helvetica 20 bold")
    p_text_2 = tk.Label(left, text=None, background=BACKGROUND_COLOR, wraplength=X_IMAGE - 20, fg=TEXT_COLOR)
    p_text_3_title = tk.Label(left, text=title_3, background=BACKGROUND_COLOR, wraplength=X_IMAGE - 20,
                              fg=TEXT_COLOR, font="Helvetica 20 bold")
    p_text_3 = tk.Label(left, text=None, background=BACKGROUND_COLOR, wraplengt=X_IMAGE - 20, fg=TEXT_COLOR)
    p_text_1_title.pack(side=tk.TOP, fill="both", expand="yes")
    p_text_1.pack(side=tk.TOP, fill="both", expand="yes", pady=(0, 10))
    p_text_2_title.pack(side=tk.TOP, fill="both", expand="yes")
    p_text_2.pack(side=tk.TOP, fill="both", expand="yes", pady=(0, 10))
    p_text_3_title.pack(side=tk.TOP, fill="both", expand="yes")
    p_text_3.pack(side=tk.TOP, fill="both", expand="yes", pady=(0, 15))

    init_colors()
    pie_1 = init_pie(right, tk.BOTTOM, "VISUAL TAGS ANALYSIS", "center")
    pie_2 = init_pie(right, tk.BOTTOM, "ORIGINAL TAGS ANALYSIS", "center")
    button_quit = init_button(window, "QUIT", bottom, "right", window.destroy)

    global default_chart

    if iterative:
        button_next = init_button(window, "NEXT", bottom, "left")
        return window, panel_image, pie_1, pie_2, p_text_1, p_text_2, p_text_3, button_next, button_quit
    return window, panel_image, pie_1, pie_2, p_text_1, p_text_2, p_text_3, button_quit


def init_reduced_window(title, pie_title, pie_title_value, pie_values, pie_labels, text=None, image_path=None):
    window = tk.Tk()
    window.resizable(False, False)
    window.title(title)
    if image_path is not None or text is not None:
        left = tk.Frame(window, background=BACKGROUND_COLOR)
        left.pack(side="left")
        if image_path is not None:
            panel_image = tk.Label(left, image=None)
            panel_image.pack(side=tk.LEFT, fill="both", expand="no", padx=20)
            update_img(panel_image, image_path)
        if text is not None:
            tk.Label(left, text=text, background=BACKGROUND_COLOR, wraplength=X_IMAGE - 20, fg=TEXT_COLOR,
                     font="Helvetica 20 bold")
    pie = init_pie(window, tk.RIGHT, pie_title, "center")
    update_pie(pie, pie_values, pie_labels, pie_title, pie_title_value)


def init_pie(window, side, title, anchor):
    figure1 = Figure(figsize=(9, 4), dpi=100, facecolor=BACKGROUND_COLOR)
    figure1.suptitle(title, fontweight="bold", horizontalalignment="center", x=0.51, y=0.95, color=TEXT_COLOR)
    subplot1 = figure1.add_subplot(111)  # add a subplot
    subplot1.pie(x=[], wedgeprops=dict(width=0.5), startangle=-40, shadow=True, autopct='%1.1f%%')
    subplot1.axis('equal')
    subplot1.set_prop_cycle(color=COLORS)
    figure1.subplots_adjust(left=-0.3)
    pie = FigureCanvasTkAgg(figure1, window)  # create a canvas figure (matplotlib module)
    pie.get_tk_widget().pack(side=side, fill=tk.BOTH, anchor=anchor)
    return figure1


def init_button(window, text, position, side, command=None):
    button = tk.Button(window, text=text, width=10, height=2, command=command)
    button.pack(in_=position, side=side)
    return button


def update_pie(figure, pie_values, pie_labels, title, title_value, percent_values=True):
    subplot = figure.subplots()
    for text in figure.texts:
        if text.get_position() == (0.3, 0.5) or text.get_position() == (0.5, 0.5):
            text.remove()
    subplot.remove()  # subplot.clear()
    subplot = figure.add_subplot(111)
    subplot.set_title(title, y=0.38, color=TEXT_COLOR)
    figure.text(x=0.3, y=0.5, s=title_value, color=TEXT_COLOR, fontsize=40, horizontalalignment='center')
    circle = plt.Circle((0, 0), 0.48, color=GREEN if int(title_value) > 0 else RED)
    subplot.add_patch(circle)
    pie_values = np.around(pie_values, 3).tolist()
    wedges, texts = subplot.pie(pie_values, wedgeprops=dict(width=0.5), startangle=-40)
    subplot.set_prop_cycle(color=COLORS)
    if percent_values:
        pie_values = [str(pie_val) + "%" for pie_val in pie_values]
    subplot.legend(wedges, ["{}: {}".format(l, v) for l, v in zip(pie_labels, pie_values)],
                   title="EMOTIONS",
                   loc="best",
                   bbox_to_anchor=(0.55, 0, 0.5, 1),
                   ncol=2,
                   fancybox=True)

    subplot.axis('equal')
    figure.canvas.draw_idle()
    return figure


def reset_pie(figure):
    subplot = figure.subplots()
    for text in figure.texts:
        if text.get_position() == (0.3, 0.5) or text.get_position() == (0.5, 0.5):
            text.remove()
    subplot.remove()  # subplot.clear()
    figure.text(x=0.5, y=0.5, s=RESET_MESSAGE, color=RED, fontsize=20, horizontalalignment='center')
    figure.canvas.draw_idle()
    return figure


def update_text(t_label, text, width=None):
    t_label.configure(text=limit_text(text, width))


def update_button(button, func):
    button.configure(command=func)


def popup_msg(window, title, label, command=None):
    qw = tk.Tk()
    qw.resizable(False, False)
    qw.title(title)
    qw.configure(background=BACKGROUND_COLOR, borderwidth=1)
    frame1 = tk.Frame(qw, background=BACKGROUND_COLOR)
    frame1.pack()
    width = 300
    height = 70 if command is None else 120
    pos_x = int(window.winfo_x() + (window.winfo_width() - width) / 2)
    pos_y = int(window.winfo_y() + (window.winfo_height() - height) / 2)
    qw.geometry("{}x{}+{}+{}".format(width, height, pos_x, pos_y))
    lbl = tk.Label(frame1, text=label, background=BACKGROUND_COLOR, fg=TEXT_COLOR, pady=25)
    lbl.pack()
    qw.call('wm', 'attributes', '.', '-topmost', '1')
    qw.overrideredirect(1)
    if command is not None:
        btn = tk.Button(frame1, text="OK", bg="light blue", fg="red", command=command, width=10, bd=0)
        btn.pack(padx=10, pady=10, side=tk.BOTTOM)
        qw.mainloop()
    else:
        qw.update()
    return qw


def update(window, image_canvas, p1_canvas, p2_canvas, b1_canvas, t3_label, t4_label, t5_label, update_command):
    try:
        image_title, image_path, p1_val, p1_lab, p2_val, p2_lab, t1, t2, t3, t4, t5 = next(update_command)
        window.title(image_title)
        update_img(image_canvas, image_path)
        p1_canvas = update_pie(p1_canvas, p1_val, p1_lab, "% SENTIMENT", str(percentage(t1, 2)))
        p2_canvas = update_pie(p2_canvas, p2_val, p2_lab, "% SENTIMENT", str(percentage(t2, 2)))
        update_text(t3_label, t3, 30)
        update_text(t4_label, t4, 30)
        update_text(t5_label, t5, 30)
        update_button(b1_canvas,
                      lambda: update(window, image_canvas, p1_canvas, p2_canvas, b1_canvas, t3_label, t4_label,
                                     t5_label, update_command))
    except StopIteration:
        popup_msg(window, "INFO", "No more element! Click Ok to exit.", command=quit)
        window.destroy()

    window.mainloop()


def update_full(window, image_canvas, p1_canvas, p2_canvas, b1_canvas, t3_label, t4_label, t5_label, update_command):
    try:
        global wait_popup
        if wait_popup is not None:
            wait_popup = popup_msg(window, "WAIT", "Processing...")
        tags_sent, tags_emo, tags_rel, image_sent, image_emo, title, path, original_tags, visual_tags = next(
            update_command)

        window.title(title)
        update_img(image_canvas, path)

        p1_lab, p1_val = list(image_emo.keys()), list(image_emo.values()) if image_emo else (None, None)
        p2_lab, p2_val = list(tags_emo.keys()), list(tags_emo.values()) if tags_emo else (None, None)
        if image_emo:
            image_sent = list(image_sent.values())
            image_sent_percent = percentage(image_sent[0], 2) if image_sent else 0
            update_pie(p1_canvas, [percentage(val, 1, integer=False) for val in p1_val], p1_lab, "% SENTIMENT",
                       image_sent_percent)
        else:
            reset_pie(p1_canvas)
        if tags_emo:
            tags_sent = list(tags_sent.values())
            tags_sent_percent = percentage(tags_sent[0], 2) if tags_sent else 0
            update_pie(p2_canvas, [percentage(val, 1, integer=False) for val in p2_val], p2_lab, "% SENTIMENT",
                       tags_sent_percent)
        else:
            reset_pie(p2_canvas)

        # p1_canvas = update_pie(p1_canvas, p1_val, p1_lab, "% SENTIMENT",
        #                        percentage(list(image_sent.values())[0], 2)) if image_sent else None
        # p2_canvas = update_pie(p2_canvas, p2_val, p2_lab, "% SENTIMENT",
        #                        percentage(list(tags_sent.values())[0], 2)) if tags_sent else None
        update_text(t3_label, str(percentage(tags_rel, 100, integer=False)) + "%", 30)
        update_text(t4_label, " ".join(original_tags), 200)
        update_text(t5_label, " ".join(visual_tags), 200)
        update_button(b1_canvas,
                      lambda: update_full(window, image_canvas, p1_canvas, p2_canvas, b1_canvas, t3_label, t4_label,
                                          t5_label, update_command))
        if wait_popup is not None:
            wait_popup.destroy()
        else:
            wait_popup = True
    except StopIteration:
        popup_msg(window, "INFO", "No more element! Click Ok to exit.")
        window.destroy()
    window.deiconify()
    window.mainloop()


def single_instance_window(title, image_emo, image_sent, tags_emo, tags_sent, tags_rel, usr_id, usr_name, usr_img_path):
    """
    :param usr_img_path:
    :param usr_name:
    :param usr_id:
    :param title: string
    :param image_emo: dict
    :param image_sent: dict
    :param tags_emo: dict
    :param tags_sent: dict
    :param tags_rel: float
    :param usr_img_path: string
    :return:
    """
    window, panel_image, pie_1, pie_2, p_text_1, p_text_2, p_text_3, _ = init_full_window(iterative=False,
                                                                                          title_1="USER ID",
                                                                                          title_2="USER NAME",
                                                                                          title_3="DESCRIPTIVE CAPACITY"
                                                                                                  "\nOF THE USER")

    window.title(title)
    try:
        update_img(panel_image, usr_img_path[0])
    except OSError:
        os.remove(usr_img_path[0])
        update_img(panel_image, usr_img_path[1])
    update_text(p_text_1, usr_id)
    update_text(p_text_2, usr_name)
    update_text(p_text_3, str(percentage(tags_rel, 100, integer=False)) + "%")
    p1_lab, p1_val = list(image_emo.keys()), list(image_emo.values()) if image_emo else (None, None)
    p2_lab, p2_val = list(tags_emo.keys()), list(tags_emo.values()) if tags_emo else (None, None)
    if image_emo:
        image_sent = list(image_sent.values())
        image_sent_percent = percentage(image_sent[0], 2) if image_sent else 0
        update_pie(pie_1, [percentage(val, 1, integer=False) for val in p1_val], p1_lab, "% SENTIMENT",
                   image_sent_percent)
    else:
        reset_pie(pie_1)
    if tags_emo:
        tags_sent = list(tags_sent.values())
        tags_sent_percent = percentage(tags_sent[0], 2) if tags_sent else 0
        update_pie(pie_2, [percentage(val, 1, integer=False) for val in p2_val], p2_lab, "% SENTIMENT",
                   tags_sent_percent)
    else:
        reset_pie(pie_2)
    window.deiconify()
    window.mainloop()


def test_func():
    image_path_1 = "./image_test/dog.jpg"
    image_path_2 = "./image_test/birds.jpg"
    values_1 = [np.around(x, 3) for x in np.arange(1, 2, 1 / 24)]
    labels_1 = ["emotion : {}".format(x) for x in values_1]
    values_2 = [np.around(x, 3) for x in np.arange(0, 1, 1 / 24)]
    labels_2 = ["emotion : {}".format(x) for x in values_2]
    values_3 = [x for x in range(51, 75)]
    labels_3 = ["emotion : {}".format(x) for x in values_3]
    values_4 = [x for x in range(76, 100)]
    labels_4 = ["emotion : {}".format(x) for x in values_4]
    sss = "qwertyuioplkjhgfdsazxcvbnm1234567890.0987654321"
    sol1 = "IMAGE 1", image_path_1, values_1, labels_1, values_2, labels_2, "-0.2", "0.6", "SENTIMENT", sss, "OL"
    sol2 = "IMAGE 2", image_path_2, values_3, labels_3, values_4, labels_4, "-1.2", "1.29", "SALSA", "REX", "AXIS"
    sol3 = "IMAGE 2", image_path_1, values_2, labels_3, values_3, labels_3, "0", "1.4", "SALSA", "REX", "AXIS"
    for x in (sol1, sol2, sol3):
        yield x


if __name__ == "__main__":
    texts_test = ["TAGS RELIABILITY", "ORIGINAL TAGS", "VISUAL TAGS"]
    w, image_t, pie_1_t, pie_2_t, text_3, text_4, text_5, button_1_t, _ = init_full_window(title_1="TAGS RELIABILITY",
                                                                                           title_2="ORIGINAL TAGS",
                                                                                           title_3="VISUAL TAGS")
    generator = test_func()
    update(w, image_t, pie_1_t, pie_2_t, button_1_t, text_3, text_4, text_5, update_command=generator)
