""" Implementation of geoplots with Geopandas
"""

import datetime
import typing
from typing import Mapping

import attr
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.units as munits
import numpy as np
import pandas as pd
import geopandas
from matplotlib import colors, ticker, transforms
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Colormap

from ._base_chart import _BaseChart


@attr.s
class MapChart(_BaseChart):
    """
    Map chart using Geopandas

    Args:
        _BaseChart ([type]): Base chart for all chart classes

    Raises:
        ValueError: [description]
    """

    enable_basemap: bool = attr.ib()

    def __attrs_post_init__(self):
        """ Properties to be determined after initialization
        """
        self.df = self.df.copy()

        # Convert all columns except geometry to datetime
        try:
            self.df = self.convert_data_cols_to_datetime(self.df)
            self.df = self.get_interpolated_geo_df(self.df)
        except:
            import warnings

            warnings.warn(
                "Pandas_Alive failed to convert columns to datetime, setting interpolate_period to False and retrying..."
            )
            self.interpolate_period = False
            self.df = self.get_interpolated_geo_df(self.df)

        temp_gdf = self.df.copy()
        self.df = pd.DataFrame(self.df)
        self.df = self.df.drop("geometry", axis=1)

        if self.fig is None:
            self.fig, self.ax = self.create_figure()
            self.figsize = self.fig.get_size_inches()
        else:
            self.fig = plt.figure()
            self.ax = plt.axes()
        self.fig.set_tight_layout(False)
        if self.title:
            self.ax.set_title(self.title)
        if self.enable_progress_bar:
            self.setup_progress_bar()

        self.df = temp_gdf

    def get_data_cols(self, gdf: geopandas.GeoDataFrame) -> typing.List:
        """
        Get data columns from GeoDataFrame (this excludes geometry)

        Args:
            gdf (geopandas.GeoDataFrame): Input GeoDataframe

        Returns:
            typing.List: List of columns except geometry
        """
        return gdf.loc[:, gdf.columns != "geometry"].columns.tolist()

    def convert_data_cols_to_datetime(
        self, gdf: geopandas.GeoDataFrame
    ) -> geopandas.GeoDataFrame:
        """
        Convert all data columns to datetime with `pd.to_datetime`

        Args:
            gdf (geopandas.GeoDataFrame): Input GeoDataFrame

        Returns:
            geopandas.GeoDataFrame: GeoDataFrame with data columns converted to `Timestamp`
        """
        converted_column_names = []
        for col in gdf.columns:
            if col != "geometry":
                col = pd.to_datetime(col)

            converted_column_names.append(col)
        gdf.columns = converted_column_names
        return gdf

    def get_interpolated_geo_df(
        self, gdf: geopandas.GeoDataFrame
    ) -> geopandas.GeoDataFrame:
        """
        Interpolates GeoDataFrame by splitting data from geometry, interpolating and joining back together

        Args:
            gdf (geopandas.GeoDataFrame): Input GeoDataFrame

        Returns:
            geopandas.GeoDataFrame: Interpolated GeoDataFrame
        """

        # Separate data from geometry
        temp_df = pd.DataFrame(gdf)
        temp_df = temp_df.drop("geometry", axis=1)
        temp_df = temp_df.T
        geometry_column = gdf.geometry

        # Interpolate data
        interpolated_df = super().get_interpolated_df(
            temp_df, self.steps_per_period, self.interpolate_period
        )

        # Rejoin data with geometry
        interpolated_df = interpolated_df.T
        interpolated_df["geometry"] = geometry_column

        return geopandas.GeoDataFrame(interpolated_df)

    def plot_geo_data(self, i: int, gdf: geopandas.GeoDataFrame) -> None:
        # fig, ax = plt.subplots(figsize=(5,3), dpi=100)
        # self.ax.clear()
        column_to_plot = gdf.columns[i]
        gdf.plot(
            column=column_to_plot,
            ax=self.ax,
            markersize=gdf[column_to_plot],
            cmap="viridis",
        )

        if self.enable_basemap:
            try:
                import contextily

                contextily.add_basemap(
                    self.ax, source=contextily.providers.CartoDB.Positron
                )
            except ImportError:
                import warnings

                warnings.warn(
                    "Ensure contextily is installed for basemap functionality https://github.com/geopandas/contextily"
                )

        return self.ax

    def anim_func(self, i: int) -> None:
        """ Animation function

        Args:
            i (int): Index of frame of animation
        """
        if self.enable_progress_bar:
            self.update_progress_bar()

        self.ax.clear()
        # for path in self.ax.collections:
        #     path.remove()
        self.plot_geo_data(i, self.df)
        if self.period_fmt:
            self.show_period(i)

    def init_func(self) -> None:
        """ Initialization function for animation
        """
        column_to_plot = self.df.columns[0]
        self.df.plot(
            column=column_to_plot,
            markersize=self.df[column_to_plot],
            # cmap='viridis',
        )
        # self.ax.scatter([], [])

    def get_frames(self):
        return range(len(self.df.columns))
