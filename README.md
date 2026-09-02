![Screenshot of rendering](./resources/solar_system.png?raw=true "Screenshot of rendering")

# Overview

A simple OpenGL 3D rendering of a miniature solar system featuring textured celestial bodies, dynamic lighting, and an orbiting camera.

The scene consists of:

- **Sun** – Located at the world origin and serves as the primary point light source.
- **Earth** – Orbits around the Sun.
- **Moon** – Orbits around the Earth.
- **Sirius** – A secondary blue point light source that continuously orbits the system. Named after [brightest star in the night sky](https://en.wikipedia.org/wiki/Sirius).

Features include:

- Textured sphere models for all celestial bodies.
- Orthographic projection to preserve the spherical appearance of planets.
- A user-controlled camera that can orbit around the system.
- Per-fragment lighting using the Phong Reflection Model (ambient, diffuse, and specular components).
- Multiple coloured light sources whose contributions are accumulated to determine the final fragment colour.

# Setup
Setup assumes that you are using a UNIX-based OS with python3 and python3-venv installed.

To build the virtual environment and install necessary packages:

```
> make
```

To activate the virtual environment:

```
> source ./venv/bin/activate
```

# Running
To run the program:

```
> python ./src/main.py
```

# Controls
Q: Exit program

P: Pause/Unpause

T: Increase orbit speed

R: Decrease orbit speed

A: Rotate camera left

D: Rotate camera right

# Troubleshooting

If the pygame installation is causing issues on Windows, install `pygame-ce` instead with:

```
> pip intall pygame-ce
```