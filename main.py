from PIL import Image, ImageDraw
from collections import Counter
import heapq
import sys

MODE_RECTANGLE = 1
MODE_ELLIPSE = 2
MODE_ROUNDED_RECTANGLE = 3

MODE = MODE_RECTANGLE
ITERATIONS = 1024
LEAF_SIZE = 4
PADDING = 1
FILL_COLOR = (0, 0, 0)
SAVE_FRAMES = False
ERROR_RATE = 0.5
AREA_POWER = 0.25
OUTPUT_SCALE = 1

def weighted_average(hist):
    total = sum(hist)
    value = sum(i * x for i, x in enumerate(hist)) / total
    error = sum(x * (value - i) ** 2 for i, x in enumerate(hist)) / total
    error = error ** 0.5
    return value, error

def color_from_histogram(hist):
    r, re = weighted_average(hist[:256])
    g, ge = weighted_average(hist[256:512])
    b, be = weighted_average(hist[512:768])
    e = re * 0.2989 + ge * 0.5870 + be * 0.1140
    return (int(r), int(g), int(b)), e

def rounded_rectangle(draw, box, radius, color):
    l, t, r, b = box
    d = radius * 2
    draw.ellipse((l, t, l + d, t + d), color)
    draw.ellipse((r - d, t, r, t + d), color)
    draw.ellipse((l, b - d, l + d, b), color)
    draw.ellipse((r - d, b - d, r, b), color)
    d = radius
    draw.rectangle((l, t + d, r, b - d), color)
    draw.rectangle((l + d, t, r - d, b), color)

class Quad(object):
    def __init__(self, model, box, depth):
        self.model = model
        self.box = box
        self.depth = depth
        hist = self.model.im.crop(self.box).histogram()
        self.color, self.error = color_from_histogram(hist)
        self.leaf = self.is_leaf()
        self.area = self.compute_area()
        self.children = []
    def is_leaf(self):
        l, t, r, b = self.box
        return int(r - l <= LEAF_SIZE or b - t <= LEAF_SIZE)
    def compute_area(self):
        l, t, r, b = self.box
        return (r - l) * (b - t)
    def split(self):
        l, t, r, b = self.box
        lr = l + (r - l) / 2
        tb = t + (b - t) / 2
        depth = self.depth + 1
        tl = Quad(self.model, (l, t, lr, tb), depth)
        tr = Quad(self.model, (lr, t, r, tb), depth)
        bl = Quad(self.model, (l, tb, lr, b), depth)
        br = Quad(self.model, (lr, tb, r, b), depth)
        self.children = (tl, tr, bl, br)
        return self.children
    def get_leaf_nodes(self, max_depth=None):
        if not self.children:
            return [self]
        if max_depth is not None and self.depth >= max_depth:
            return [self]
        result = []
        for child in self.children:
            result.extend(child.get_leaf_nodes(max_depth))
        return result

    def __lt__(self, other):
        l, t, r ,b = self.box
        o_l, o_t, o_r, o_b = other.box
        h = b - t
        w = r - l
        size = h * w
        o_h = o_b - o_t
        o_w = o_r - o_l
        o_size = o_h* o_w
        return size < o_size

class Model(object):
    def __init__(self, image):
        if isinstance(image, Image.Image):
            self.im = image
        else:
            self.im = Image.open(path).convert('RGB')
        self.width, self.height = self.im.size
        self.heap = []
        self.root = Quad(self, (0, 0, self.width, self.height), 0)
        self.error_sum = self.root.error * self.root.area
        self.push(self.root)
    @property
    def quads(self):
        return [x[-1] for x in self.heap]
    def average_error(self):
        return self.error_sum / (self.width * self.height)
    def push(self, quad):
        score = -quad.error * (quad.area ** AREA_POWER)
        heapq.heappush(self.heap, (quad.leaf, score, quad))
    def pop(self):
        return heapq.heappop(self.heap)[-1]
    def split(self):
        quad = self.pop()
        self.error_sum -= quad.error * quad.area
        children = quad.split()
        for child in children:
            self.push(child)
            self.error_sum += child.error * child.area
    def render(self, path, max_depth=None):
        m = OUTPUT_SCALE
        dx, dy = (PADDING, PADDING)
        im = Image.new('RGB', (self.width * m + dx, self.height * m + dy))
        draw = ImageDraw.Draw(im)
        draw.rectangle((0, 0, self.width * m, self.height * m), FILL_COLOR)
        for quad in self.root.get_leaf_nodes(max_depth):
            l, t, r, b = quad.box
            box = (int(l * m + dx), int(t * m + dy), int(r * m - 1), int(b * m - 1))
            if MODE == MODE_ELLIPSE:
                draw.ellipse(box, quad.color)

            elif MODE == MODE_ROUNDED_RECTANGLE:
                radius = m * min((r - l), (b - t)) / 4
                rounded_rectangle(draw, box, radius, quad.color)
            else:
                draw.rectangle(box, quad.color)
        del draw
        if path:
            im.save(path, 'PNG')
        else:
            return im

def main(image, mode = 2, iterations=ITERATIONS, leaf_size = 4, padding = 1, fill_color = (0,0,0), error_rate= 0.5, area_power = 0.25, output_scale = 1):
    global MODE
    global ITERATIONS
    global LEAF_SIZE
    global PADDING
    global FILL_COLOR
    global SAVE_FRAMES
    global ERROR_RATE
    global AREA_POWER
    global OUTPUT_SCALE
    ITERATIONS = iterations
    MODE = mode
    LEAF_SIZE = leaf_size
    PADDING = padding
    FILL_COLOR = fill_color
    FILL_COLOR = tuple([int(el) for el in fill_color])
    ERROR_RATE = error_rate
    AREA_POWER = area_power
    OUTPUT_SCALE = output_scale

    model = Model(image)
    previous = None
    for i in range(iterations):
        error = model.average_error()
        if previous is None or previous - error > ERROR_RATE:
            print(i, error)
            if SAVE_FRAMES:
                model.render('frames/%06d.png' % i)
            previous = error
        model.split()
    return model.render(path=None)
    print('-' * 32)
    depth = Counter(x.depth for x in model.quads)
    for key in sorted(depth):
        value = depth[key]
        n = 4 ** key
        pct = 100.0 * value / n
        print('%3d %8d %8d %8.2f%%' % (key, n, value, pct))
    print('-' * 32)
    print('             %8d %8.2f%%' % (len(model.quads), 100))
    # for max_depth in range(max(depth.keys()) + 1):
    #     model.render('out%d.png' % max_depth, max_depth)

if __name__ == '__main__':
    main()
