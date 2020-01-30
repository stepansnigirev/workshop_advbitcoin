# Prerequisites

* Your laptop preferably with [Jupyter Notebook](https://jupyter.org/)
* The board, or [online simulator](https://diybitcoinhardware.com/f469-disco/simulator/)

Basically covers this tutorial:

https://github.com/diybitcoinhardware/f469-disco/tree/master/docs/tutorial

Also in a lecture-style our video series:

https://www.youtube.com/playlist?list=PLn2qRQUAAg0z_-R0swVuSsNS9bzRu6oP5

# Setting up the board

- Install jupyter notebook: `pip3 install jupyterlab`
- Clone the repo `git clone --recursive https://github.com/diybitcoinhardware/f469-disco.git`
- Install jupyter kernel: [howto](https://github.com/diybitcoinhardware/f469-disco/tree/master/jupyter_kernel)
- Download and upload to the board (`DIS_F469` volume) the latest release of our [micropython build](https://github.com/diybitcoinhardware/f469-disco/releases/download/1.0.0/upy-f469disco.bin)
- Run Jupyter and create a new document with `F469 Micropython Kernel`

Now you have interactive juputer notebook talking to the board!