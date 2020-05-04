from pandas_alive.charts import BarChart, BaseChart, LineChart
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
from typing import List, Union


def load_dataset(name: str = "covid19") -> pd.DataFrame:
    """ Returns a pandas DataFrame suitable for immediate use in `pandas-alive`

    Args:
        name (str, optional): Name of dataset to load. Either 'covid19' or 'urban_pop'. Defaults to 'covid19'.

    Returns:
        pd.DataFrame: Loaded DataFrame
    """

    return pd.read_csv(
        f"https://raw.githubusercontent.com/JackMcKew/pandas-alive/master/data/{name}.csv",
        index_col=0,
        parse_dates=[0],
    )

