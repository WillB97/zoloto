from typing import Optional

from cached_property import cached_property
from cv2 import aruco
from fastcache import clru_cache
from numpy import array, linalg

from .calibration import CalibrationParameters
from .coords import Coordinates, Orientation, ThreeDCoordinates


class Marker:
    def __init__(
        self,
        id,
        corners,
        size: int,
        calibration_params: Optional[CalibrationParameters] = None,
        precalculated_vectors=None,
    ):
        self.__id = int(id)
        self.__pixel_corners = corners
        self.__size = size
        self.__camera_calibration_params = calibration_params
        self.__precalculated_vectors = precalculated_vectors

    @property
    def id(self):
        return self.__id

    @property
    def size(self):
        return self.__size

    def _is_eager(self):
        return bool(self.__precalculated_vectors)

    @property
    def pixel_corners(self):
        return [Coordinates(*coords) for coords in self.__pixel_corners]

    @cached_property
    def pixel_centre(self):
        tl, _, br, _ = self.__pixel_corners
        return Coordinates([tl[0] + (self.__size / 2) - 1, br[1] - (self.__size / 2)])

    @cached_property
    def distance(self):
        return int(linalg.norm(self._tvec))

    @property
    def orientation(self):
        return Orientation(*self._rvec)

    @property
    def cartesian(self):
        return ThreeDCoordinates(*self._tvec)

    @clru_cache(maxsize=None)
    def _get_pose_vectors(self):
        if self._is_eager():
            return self.__precalculated_vectors

        rvec, tvec, _ = aruco.estimatePoseSingleMarkers(
            [self.__pixel_corners], self.__size, *self.__camera_calibration_params
        )
        return rvec[0][0], tvec[0][0]

    @property
    def _rvec(self):
        rvec, _ = self._get_pose_vectors()
        return rvec

    @property
    def _tvec(self):
        _, tvec = self._get_pose_vectors()
        return tvec

    def as_dict(self):
        return {
            "id": self.id,
            "size": self.size,
            "pixel_corners": self.__pixel_corners.tolist(),
            "rvec": self._rvec.tolist(),
            "tvec": self._tvec.tolist(),
        }

    @classmethod
    def from_dict(cls, marker_dict):
        return cls(
            marker_dict["id"],
            array(marker_dict["pixel_corners"]),
            marker_dict["size"],
            None,
            (array(marker_dict["rvec"]), array(marker_dict["tvec"])),
        )