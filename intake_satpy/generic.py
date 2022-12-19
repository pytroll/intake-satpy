from abc import ABC
from glob import glob

from intake.source.base import PatternMixin
from intake_xarray.base import DataSourceMixin

from satpy import Scene


class SatpySource(DataSourceMixin, PatternMixin, ABC):
    name = "satpy"

    def __init__(self, urlpath,
                 scene_kwargs=None,
                 load_kwargs=None,
                 resample_kwargs=None,
                 metadata=None,
                 path_as_pattern=True, **kwargs):
        self.path_as_pattern = path_as_pattern
        self.urlpath = urlpath
        self.scene_kwargs = scene_kwargs or {}
        self.load_kwargs = load_kwargs or {}
        self.resample_kwargs = resample_kwargs or {}
        self._scn = None
        self._resampled_scn = None
        self._ds = None
        super().__init__(metadata=metadata, **kwargs)

    def _open_dataset(self):
        url = self.urlpath
        if not isinstance(url, list):
            url = [url]

        url = list(self._glob_if_needed(url))
        self._scn = Scene(filenames=url, **self.scene_kwargs)
        self._scn.load(**self.load_kwargs)

        if not self.resample_kwargs:
            self.resample_kwargs["destination"] = self._scn.finest_area()
            self.resample_kwargs["resampler"] = "native"
        self._resampled_scn = self._scn.resample(**self.resample_kwargs)
        self._ds = self._resampled_scn.to_xarray_dataset()

    @staticmethod
    def _glob_if_needed(urls_or_globs):
        for url_or_glob in urls_or_globs:
            if "*" not in url_or_glob and "?" not in url_or_glob:
                yield url_or_glob
            yield from glob(url_or_glob)
