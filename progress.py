import progressbar


def eta_widget(title):
    return [
        title,
        " (",
        progressbar.SimpleProgress(),
        ") ",
        " (",
        progressbar.Timer(),
        ") ",
        " (",
        progressbar.ETA(),
        ") ",
    ]


class Bar:
    def __init__(self, title, max_size):
        self.i = 0
        self.bar = progressbar.ProgressBar(widgets=eta_widget(title), maxval=max_size)
        self.bar.start()

    def update(self, step=1):
        self.i += step
        self.bar.update(self.i)
