[![Build Status](https://travis-ci.com/xrombik/pyglwidgets.svg?branch=alpha1)](https://travis-ci.com/xrombik/pyglwidgets)
# pyglwidgets
### Main futures:
- Simple GUI engine with OpenGL;
- Fast response for user input;
- Zero draw calls if no changes;
- Custom draw callbacks.
 
### Widgets that already implemented:
- Push, check and radio buttons;
- Customized tables;
- Regulators driven by mouse move;
- Edit/entry boxes;
- Static and dynamic Unicode text;
- Pictures with scale and rotation.

<img src="https://github.com/xrombik/pyglwidgets/blob/alpha1/playground.png" width="320">

### Quick start
- Clone this repo with command:
```git clone https://github.com/xrombik/pyglwidgets```

- Go to the cloned repo directory:
```cd pyglwidgets```

- Run script that installs all dependencies (checked on `Debian 10` or `Ubuntu 18` based distros):
```./install-deps.sh```

- Run examples:

Bunch of GUI items:
```./playground.py```

Just table only:
```./table.py```

Funny red stars:
```./star.py```
