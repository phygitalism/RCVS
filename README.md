# RCVS plugin for Blender

[Video](https://youtu.be/WNpm5r5vwTQ)

## Building

1. Compile Rust program `cd ./rcvs_compare; cargo build --release`
2. Copy `rcvs_compare` from `target/release` into `blender_py`
3. Archive `blender_py` as zip archive `.zip`

##  Blender installation

```
Preferences -> Add-ons -> Install (select created zip archive) -> enable
```

## Plugin settings

In the `Properties / Scene` will be RCVS Settings.

You must choose directory with 3D objects ([OBJ](https://en.wikipedia.org/wiki/Wavefront_.obj_file)). For testing create such directory with a few objects.

Choose any object in the scene and press Search in the Properties / Object.