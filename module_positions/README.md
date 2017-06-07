# Checking the position of the velo


## Running

First modify `options.py` to specify the database which should be used, the json used by the notebook can then generated using Brunel:

```bash
lb-run Brunel/v51r1 python make_velo_geometry_json.py
```

The jupyter notebook can then be executed to produce the plots.

## Defintion of positions

`output/*.json` contains the points extracted from the dector description. This can be read using:

```python
import json
with open('output/?????.json', 'rt') as f:
    velo_geometry = json.load(f)
```

The `x`, `y` and `z` position of a point can then be extracted using `velo_geometry[MODULE_PATH][POINT]` where point is a character between A-H, corrosponding to a point below.

![Image](https://www.dropbox.com/s/s8uat2z5ywo66bm/VeloPix-Ladder-Definition.JPG?dl=1)
