

import numpy as np
import pygame as pg
import moderngl as mgl
import cProfile
import time


class pixel:
    def __init__(self, position, color):
        self.position = position
        self.color = color


# setup
pg.init()

windowWidth = 900
windowHeight = 900
screen = pg.display.set_mode((windowWidth, windowHeight), pg.OPENGL | pg.DOUBLEBUF)

renderContext = mgl.create_context()
clock = pg.time.Clock()

running = True
dt = 0

totalPixels = windowWidth * windowHeight
bufferSize = totalPixels * 3 * 4


# shaders
mathShader = renderContext.program(
    vertex_shader="""
#version 330

in vec2 inputPoint;

in ivec3 color;

out vec3 outputColor;

void main() {

    vec2 points = inputPoint;
    ivec3 colors = color;

    gl_Position = vec4(points, 0.0, 1.0);
    gl_PointSize = 1.0;

    outputColor = vec3(colors) / 255.0;
}
""",
    fragment_shader="""
#version 330

in vec3 outputColor;

out vec4 fragmentColor;

void main() {
    fragmentColor = vec4(outputColor, 1.0);
}
"""
)


# array creation
def createInputArray():
    # creates triangle vertices from quads
    
    xValues = np.linspace(-1, 1, int(windowWidth / 50))
    yValues = np.linspace(-1, 1, int(windowHeight / 50))
    xArray, yArray = np.meshgrid(xValues, yValues)
    inputArray = np.stack((xArray, yArray), axis=2).astype("f4")

    print(np.shape(inputArray))

    triangleList = []

    for row in range(len(inputArray) - 1):
        for column in range(len(inputArray[row]) - 1):
            v1 = inputArray[row][column]
            v2 = inputArray[row][column + 1]
            v3 = inputArray[row + 1][column]

            v4 = inputArray[row][column + 1]
            v5 = inputArray[row + 1][column + 1]
            v6 = inputArray[row + 1][column]

            triangleList.append(v1)
            triangleList.append(v2)
            triangleList.append(v3)

            triangleList.append(v4)
            triangleList.append(v5)
            triangleList.append(v6)

    inputArray = np.array(triangleList, dtype="f4")

    typeArray = genColor(inputArray)

    return inputArray,typeArray


def genColor(inputArray):

    typeArray = np.ones((len(inputArray), 3), dtype="i4")
    image = pg.image.load(r'C:\Users\pilot\Desktop\colorpallete.png')
    colorArray = pg.surfarray.array3d(image)

    colorArray = colorArray.reshape(-1, 3).astype("i4")

    for i in range(0, len(typeArray), 6):
            if inputArray[i,1] < -.3:
                typeArray[i:i + 6] = colorArray[6]
                if inputArray[i,1] < -.5:
                    typeArray[i:i + 6] = colorArray[8]
            else:
                typeArray[i:i + 6] = colorArray[3]  
    return typeArray


# shader running
def runShader(pointArray,typeArray):
    # sends the input array to the shader

    pointBuffer = renderContext.buffer(pointArray.astype("f4").tobytes())
    typeBuffer = renderContext.buffer(typeArray.astype("i4").tobytes())

    vertexArray = renderContext.vertex_array(mathShader, [(pointBuffer, "2f", "inputPoint"),(typeBuffer, "3i", "color") ])

    return vertexArray


# frame creation
def createFrame():
    # builds the vertex array for the current frame

    inputArray,typeArray = createInputArray()
    
    frameArray = runShader(inputArray,typeArray)
    return frameArray


def drawFrame():
    # draws the current frame array to the pygame window

    frameArray = createFrame()
    
    renderContext.clear(0.0, 0.0, 0.0, 1.0)
    frameArray.render(mgl.TRIANGLES)
    pg.display.flip()


# input
def getMovement():
    # returns a direction code based on the held movement key

    keys = pg.key.get_pressed()

    movement = None

    if keys[pg.K_d]:
        movement = (0, 1)

    elif keys[pg.K_a]:
        movement = (1, 0)

    elif keys[pg.K_w]:
        movement = (1, 1)

    elif keys[pg.K_s]:
        movement = (0, 0)

    return movement


# main loop
def main():
    running = True
    dt = 0

    drawFrame()

    while running:
        for event in pg.event.get():
            print(event)

            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN:
                print("keydown")

                movement = getMovement()

                if movement != None:
                    print(movement)
                    drawFrame()

        dt = clock.tick(60) / 1000

    pg.font.quit()
    pg.quit()


cProfile.run("main()", sort="cumtime")
