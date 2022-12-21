from abc import ABC
from glob import glob

import s3fs
from intake.source.base import PatternMixin
from intake_xarray.base import DataSourceMixin
from satpy import MultiScene
from satpy.multiscene import timeseries


class SatpySource(DataSourceMixin, PatternMixin, ABC):
    name = "satpy"

    def __init__(
        self,
        urlpath,
        grouping_kwargs=None,
        scene_kwargs=None,
        load_kwargs=None,
        resample_kwargs=None,
        metadata=None,
        path_as_pattern=True,
        **kwargs,
    ):
        self.path_as_pattern = path_as_pattern
        self.urlpath = urlpath
        self.grouping_kwargs = grouping_kwargs or {}
        self.scene_kwargs = scene_kwargs or {}
        self.load_kwargs = load_kwargs or {}
        self.resample_kwargs = resample_kwargs or {}
        self._mscn = None
        self._resampled_mscn = None
        self._scn = None
        self._ds = None
        super().__init__(metadata=metadata, **kwargs)

    def _open_dataset(self):
        url = self.urlpath
        if not isinstance(url, list):
            url = [url]

        url = list(self._glob_if_needed(url))
        self.grouping_kwargs.setdefault("reader", self.scene_kwargs.get("reader"))
        self._mscn = MultiScene.from_files(url, scene_kwargs=self.scene_kwargs, **self.grouping_kwargs)

        if "wishlist" not in self.load_kwargs:
            self.load_kwargs["wishlist"] = self._mscn.first_scene.available_dataset_ids()
        self._mscn.load(**self.load_kwargs)

        if not self.resample_kwargs:
            self.resample_kwargs["destination"] = self._mscn.first_scene.finest_area()
            self.resample_kwargs["resampler"] = "native"
        self._resampled_mscn = self._mscn.resample(**self.resample_kwargs)
        self._scn = self._resampled_mscn.blend(timeseries)
        self._ds = self._scn.to_xarray_dataset()

    @staticmethod
    def _glob_if_needed(urls_or_globs):
        for url_or_glob in urls_or_globs:
            if "*" not in url_or_glob and "?" not in url_or_glob:
                yield url_or_glob
            if url_or_glob.startswith("s3://"):
                fs = s3fs.S3FileSystem(anon=True)
                for url in fs.glob(url_or_glob):
                    yield "s3://" + url
                continue
            yield from glob(url_or_glob)
