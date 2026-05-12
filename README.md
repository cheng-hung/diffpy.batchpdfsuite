# diffpy.batchpdfsuite

Here is a quick tutorial on how to locally install the package.

## How to install `diffpy.batchpdfsuite` locally

Create and activate a new conda environment:

```bash
conda create -n diffpy.batchpdfsuite_env python=3.13 pip
conda activate diffpy.batchpdfsuite_env
```

### Install `diffpy.apps` dependency

```bash
git clone https://github.com/diffpy/diffpy.apps
cd diffpy.apps
conda install --file requirements/conda.txt
pip install .
```

### Install `diffpy.batchpdfsuite`

It's simple. The only command required is the following:

```bash
git clone https://github.com/diffpy/diffpy.batchpdfsuite
cd diffpy.batchpdfsuite
conda install --file requirements/conda.txt
pip install .
```

> The above command will automatically install the dependencies listed in `requirements/pip.txt`.

## Verify your package has been installed

Verify the installation:

```bash
pip list
```

Great! The package is now importable in any Python scripts located on your local machine.
