"""Functions to facilitate the Guinness price geographic variation analysis."""

import guindex
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point
import numpy as np
from joypy import joyplot


def get_guindex_pint_data(county, years):
    """Use the guindex package to get the pints submitted for a chosen county
    within the years specified."""

    pints_df = guindex.pints(county=county)

    pints_df = pints_df.loc[pints_df["creation_date"].dt.year.isin(years)]

    return pints_df


def load_prepare_shapefiles(shapefile_path, code_name_mapping, projection):
    """Loads in the shapefile with the postal regions and selects the codes
    that correspond to Dublin regions and adds nice names for them. Converts
    the projection used to the desired format."""

    shp = gpd.read_file(shapefile_path)

    shp.rename(
        columns={
            "RoutingKey": "routing_key",
            "Descriptor": "descriptor",
        },
        inplace=True,
    )

    shp = shp.loc[shp["routing_key"].isin(code_name_mapping.keys())]

    shp["name"] = shp["routing_key"].map(code_name_mapping)

    shp = shp.to_crs(projection)

    return shp


def sort_pubs_into_postal_regions(pub_info_df, postal_region_shapes):
    """Takes an input with all of the unique pubs that have had had pints
    submitted and uses their latitude and longitude to determine what postal
    region they are in from the shapefiles."""

    pub_info_df["postal_region"] = np.nan
    for idx, pub_info in pub_info_df.iterrows():
        pub_point = Point(pub_info["longitude"], pub_info["latitude"])
        postal_region = postal_region_shapes.loc[
            postal_region_shapes["geometry"].contains(pub_point), "name"
        ].squeeze()

        if not isinstance(postal_region, str):
            postal_region = np.nan

        pub_info_df.loc[idx, "postal_region"] = postal_region

    return pub_info_df


def pints_ridgeline(pints_df, order, save_dir, save_name):
    """Function to create a ridgeline plot showing the distribution of pint
    prices across and between Dublin postal regions."""

    fig, ax = plt.subplots()

    regions_to_plot = (
        pints_df["postal_region"]
        .value_counts()[pints_df["postal_region"].value_counts().gt(3)]
        .index.to_list()
    )
    plot_pints = pints_df.loc[pints_df["postal_region"].isin(regions_to_plot)]

    order = [x for x in order if x in regions_to_plot]
    plot_pints["postal_region"] = pd.Categorical(
        plot_pints["postal_region"], categories=order, ordered=True
    )

    fig, axs = joyplot(
        data=plot_pints, column="price", by="postal_region", overlap=0.8, ax=ax
    )

    axs[-1].set_xlabel("Price, €")
    axs[-1].set_ylabel("Dublin Postal Region")
    axs[-1].set_title(
        "Guinness Pint Prices in Dublin by Postal Region (2017-18)"
    )

    axs[-1].yaxis.set_visible(True)
    axs[-1].yaxis.set_ticks([])
    axs[-1].yaxis.set_label_position("right")

    fig.savefig(save_dir + save_name, bbox_inches="tight")

    return fig, ax


def choropleth_map(
    postal_region_shapes, column, cmap, cmap_label, save_dir, save_name
):
    fig, ax = plt.subplots()

    postal_region_shapes.plot(
        column=column,
        ax=ax,
        legend=True,
        legend_kwds={"shrink": 0.75, "label": cmap_label},
        cmap=cmap,
        edgecolor="black",
        missing_kwds={"color": "lightgray", "edgecolor": "black"},
    )
    ax.set_axis_off()

    fig.savefig(save_dir + save_name, bbox_inches="tight")

    return fig, ax
