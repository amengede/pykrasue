from OpenGL.GL import *
from PIL import Image

class Rect:
    __slots__ = (
        "width", "height", "top", 
        "left", "layer")

    def __init__(self, left: int, top: int, width: int, height: int, layer: int):

        self.width = width
        self.height = height
        self.top = top
        self.left = left
        self.layer = layer
    
    def split(self, x: int, y: int) -> tuple["Rect"]:

        x_over = self.width - x
        y_over = self.height - y

        self.width = x
        self.height = y

        return (
            Rect(self.left + x,     self.top, x_over,      y, self.layer), 
            Rect(    self.left, self.top + y,      x, y_over, self.layer), 
            Rect(self.left + x, self.top + y, x_over, y_over, self.layer))
    
    def get_area(self) -> int:

        return self.width * self.height
    
    def can_hold(self, w: int, h: int) -> bool:

        return (w <= self.width) and (h <= self.height)

    def __str__(self) -> str:

        return f"({self.left}, {self.top}, {self.width}, {self.height}, {self.layer})"

class TextureAtlas:
    """
        Manages a group of textures.
    """
    """
    __slots__ = (
        "_atlas", "_sprite_groups", "_dummy_vao", 
        "_shader", "_global_info_location",
        "_shader", "_dummy_vao", "_global_info_location")
        """

    
    def __init__(self):
        """
            Construct a new texture atlas.
        """

        self._max_w = 4096
        self._max_h = 4096
        self._history: dict[str, int] = {}
        self._free_rectangles: list[Rect] = []
        self._pending_allocations: list[Rect] = []
        self._allocated_rectangles: list[Rect] = []
        self.handle = 0
        self._layer_count = 0
        self._texture_pages: dict[int, Image.Image] = {}

    def load_image(self, filename: str) -> int:
        """
            Registers an image for loading.

            Parameters:

                filename: full filepath to the image to load.
            
            Returns:

                A handle to the loaded image, indicating the image's position
                within the set of loaded images.
        """

        if filename in self._history:
            return self._history[filename]

        i = len(self._history)
        self._history[filename] = i

        with Image.open(filename, mode = "r") as img:
            w, h = img.size
            self.allocate(Rect(0, 0, w, h, 0))

        return i
    
    def get_image_size(self, object_type: int) -> tuple[int]:
        rect = self._allocated_rectangles[object_type]
        return rect.width / 2, rect.height / 2
    
    def get_offset(self, object_type: int) -> tuple[int]:
        rect = self._allocated_rectangles[object_type]
        return rect.left, rect.top, rect.layer
    
    def get_max_size(self) -> tuple[int]:
        return self._max_w, self._max_h
    
    def build(self) -> None:

        if len(self._history) == 0:
            return
        
        # build opengl texture
        self.handle = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.handle)
        glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA8, 
                    self._max_w, self._max_h, self._layer_count, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        
        for filename, i in self._history.items():
            with Image.open(filename, mode = "r") as img:
                img = img.convert("RGBA")
                rect = self._allocated_rectangles[i]

                self._texture_pages[rect.layer].paste(img, (rect.left, rect.top))
        
        for layer, img in self._texture_pages.items():
            img_data = bytes(img.tobytes())
            w,h = img.size

            #img.save(f"page_{layer}.png")
                
            glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 
                            0, 0, layer, 
                            w, h, 1,
                            GL_RGBA,GL_UNSIGNED_BYTE,img_data)
            
            img.close()
        self._texture_pages = {}
        
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_R, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glGenerateMipmap(GL_TEXTURE_2D_ARRAY)
    
    def allocate(self, rect: Rect) -> None:

        if len(self._free_rectangles) == 0:
            self._free_rectangles.append(Rect(0, 0, self._max_w, self._max_h, self._layer_count))
            self._layer_count += 1
        
        #print(f"Rectangle: {str(rect)}")
        
        for candidate in self._free_rectangles:

            debug = candidate.layer == 0

            #if debug:
            #    print(f"Candidate: {str(candidate)}")

            if not candidate.can_hold(rect.width, rect.height):
                #if debug:
                #    print("cannot hold")
                continue
            
            #if debug:
            #    print("can hold")
            new_free_rects = candidate.split(rect.width, rect.height)
            self._free_rectangles.remove(candidate)
            self._allocated_rectangles.append(candidate)
            if candidate.layer not in self._texture_pages:
                self._texture_pages[candidate.layer] = Image.new(mode="RGBA", size=(self._max_w, self._max_h))

            for new_free_rect in new_free_rects:
                self.sorted_insert(new_free_rect, self._free_rectangles)
            
            return
        
        #print("new page")
        new_page = Rect(0, 0, self._max_w, self._max_h, self._layer_count)
        self._layer_count += 1
        new_free_rects = new_page.split(rect.width, rect.height)
        self._allocated_rectangles.append(new_page)

        if new_page.layer not in self._texture_pages:
            self._texture_pages[new_page.layer] = Image.new(mode="RGBA", size=(self._max_w, self._max_h))

        for new_free_rect in new_free_rects:
            self.sorted_insert(new_free_rect, self._free_rectangles)
    
    def sorted_insert(self, new_rect: Rect, rects: list[Rect]) -> None:

        area = new_rect.get_area()
        if area == 0:
            return

        rects.append(new_rect)
        """
        for i in range(len(rects) - 1, 1, -1):

            if rects[i - 1].get_area() > area:
                rects[i] = rects[i - 1]
            else:
                rects[i] = new_rect
                return
        
        rects[0] = new_rect
        """