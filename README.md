# Intake - Satpy Drivers

This package adds additional drivers for the
[Intake](https://intake.readthedocs.io/en/latest/) library using the
[Satpy](https://satpy.readthedocs.io/en/stable/) library to read data files.
This package also depends on
[intake-xarray](https://intake-xarray.readthedocs.io/en/latest/) to define
the Xarray container type (xarray `Dataset`) which these Satpy-based drivers
produce.

## Installation

To add this package to an existing `pip` based environment, run:

```bash
pip install intake-satpy
```

Or if you have a conda-based environment you can install it from the
conda-forge channel:

```bash
conda install -c conda-forge intake-satpy
```

## Usage

This package currently only supplies one intake driver named `satpy`.
As with any intake driver, the `satpy` driver can be used in a couple
different ways. A few examples are shown below.

### Inline Usage

Once the `intake-satpy` package is installed, you can use this driver by
calling `intake.open_satpy`. At the time of writing, it is best to provide
as much information to configure/control Satpy as you can by passing the
`scene_kwargs` and `load_kwargs`.

```
import intake
from glob import glob

data_source = intake.open_satpy(
    glob("/data/satellite/abi/*.nc"),
    scene_kwargs={"reader": "abi_l1b"},
    load_kwargs={"wishlist": ["C01"]},
)
dataset = data_source.read_chunked()
```

The `read_chunked` method will return an xarray `Dataset` object that will
contain the products that Satpy was able to create. Data will be represented
as dask arrays underneath. The `data_source.to_dask()` method will also
produce this result. The `data_source.read()` method will return the same
xarray `Dataset` object but data will be loaded into memory as numpy arrays.
Care must be taken as the large satellite formats read by Satpy can quickly
fill up your system's memory if loaded in this way.

By default, if `wishlist` is not provided as a load keyword argument
(see above), then all available "reader" level products will be loaded. This
means those that can be read directly from the file and does not include
any Satpy "composites".

Also by default the loaded dataset is "resampled" using Satpy's "native"
resampler to the finest resolution of the loaded products. This allows
for all products to exist in a single xarray `Dataset` object. This behavior
can be customized by providing `resample_kwargs` to the source creation
(`open_satpy` call).

### Catalog Usage - Local

The `satpy` driver can also be used in a catalog definition. See the
[examples/local_abi_l1b.yaml](https://github.com/pytroll/intake-satpy/blob/main/examples/local_abi_l1b.yaml)
catalog definition file for an example. With a catalog like this you could then
do:

```python
import intake

cat = intake.open_catalog("examples/local_abi_l1b.yaml")
source = cat.abi_l1b(base_dir="/data/satellite/abi")
dataset = source.read_chunked()

```

A wishlist of products to load can be provided to the source when creating it:

```python
cat = intake.open_catalog("examples/local_abi_l1b.yaml")
source = cat.abi_l1b(base_dir="/data/satellite/abi", load_kwargs={"wishlist": ["C01"]})
dataset = source.read_chunked()
```

As with the inline usage, if `wishlist` is not provided then all reader-level
products will be loaded.

### Catalog Usage - S3

Some of Satpy's readers can also read data from remote storage like S3 buckets.
An example catalog is included in the `examples/` directory of the
`intake-satpy` repository.

Note that Satpy's performance for reading S3 files is currently very slow, but
is being worked on. It is likely not suitable for loading data outside of the
network where the S3 storage is (AWS in this example) until future updates to
Satpy and NetCDF are made.

```python
import intake

cat = intake.open_catalog("examples/aws_abi_l1b_20220101_18.yaml")
source = cat.abi_l1b()
dataset = source.read_chunked()

```
