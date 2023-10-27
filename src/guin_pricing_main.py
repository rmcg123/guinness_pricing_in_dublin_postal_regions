"""
Main script for Guinness pricing geographic variation in Dublin (2017-18).
"""
import pandas as pd
from matplotlib import rcParams
import numpy as np

import guin_pricing_functions as gf
import guin_pricing_config as cfg

rcParams["font.family"] = "Arial"
rcParams["figure.figsize"] = (16, 9)
rcParams["figure.dpi"] = 300
rcParams["axes.titlesize"] = 24
rcParams["axes.labelsize"] = 16
rcParams["font.size"] = 14
rcParams["xtick.labelsize"] = 14
rcParams["ytick.labelsize"] = 14
rcParams["legend.fontsize"] = 14
rcParams["legend.title_fontsize"] = 16


def main():
    try:
        pints = pd.read_csv(cfg.DATA_FOLDER + "pints.csv")
    except FileNotFoundError:
        # Get pints from selected county for selected years from Guindex. This may
        # take a minute.
        pints = gf.get_guindex_pint_data(county=cfg.COUNTY, years=cfg.YEARS)
        pints.to_csv(cfg.DATA_FOLDER + "pints.csv")

    try:
        pubs = pd.read_csv(cfg.DATA_FOLDER + "pubs.csv")
    except FileNotFoundError:
        # Get pubs from selected county from Guindex.
        pubs = gf.get_guindex_pub_data(county=cfg.COUNTY)
        pubs.to_csv(cfg.DATA_FOLDER + "pubs.csv")

    # Load in the Shapefile that has the postal region geometry, subset to only
    # the desired ones (Dublin ones). Transform projection to desired one.
    shp = gf.load_prepare_shapefiles(
        shapefile_path=cfg.SHAPEFILE_FOLDER + cfg.SHAPEFILE_NAME,
        code_name_mapping=cfg.POSTAL_REGION_CODE_ORDER,
        projection=cfg.DESIRED_PROJECTION,
    )

    # For each of these unique pubs use the postal region shapefiles to
    # determine what postal region these pubs belong to.
    pubs = gf.sort_pubs_into_postal_regions(
        pubs_df=pubs, postal_region_shapes=shp
    )

    # Merge the postal region information back into pints DataFrame.
    pints = pints.merge(
        pubs[["pub_id", "postal_region"]], on="pub_id", how="left"
    )

    # Create a ridgeline plot of pints by postal region.
    _, _ = gf.pints_ridgeline(
        pints_df=pints,
        order=cfg.POSTAL_REGION_CODE_ORDER.values(),
        save_dir=cfg.RESULTS_FOLDER,
        save_name="ridgeline_pints.png",
    )

    # Create some summary statistics for region: average price, number of pints
    # submitted, number of pubs that have had submissions.
    region_stats = (
        pints.groupby("postal_region")
        .agg(
            n_pints=("price", "count"),
            avg_price=("price", "mean"),
            n_pubs_submitted=("pub_id", "nunique"),
        )
        .reset_index()
    )

    # Create count of pubs in each postal region.
    pub_region_counts = (
        pubs.groupby("postal_region")
        .agg(n_pubs=("pub_id", "count"))
        .reset_index()
    )

    # Merge region statistics into region shapefiles.
    shp = shp.merge(
        region_stats, how="left", left_on=["name"], right_on=["postal_region"]
    )

    # Merge region pub counts into region shapefiles.
    shp = shp.merge(
        pub_region_counts,
        how="left",
        left_on=["name"],
        right_on=["postal_region"],
    )

    # Created percentage of pubs visited
    shp["percentage_pubs_visited"] = np.where(
        shp["n_pubs"].ne(0),
        100 * shp["n_pubs_submitted"] / shp["n_pubs"],
        np.nan,
    )

    # Create some choropleth maps showing the average price, the number of
    # pints submitted and the number of pubs that have had pints submitted.
    _, _ = gf.choropleth_map(
        shp,
        column="avg_price",
        labels=False,
        cmap="YlOrRd",
        cmap_label="Average Pint Price, €",
        save_dir=cfg.RESULTS_FOLDER,
        save_name="average_price_map.png",
    )
    _, _ = gf.choropleth_map(
        shp,
        column="n_pints",
        labels=False,
        cmap="YlGnBu",
        cmap_label="Number of Pints Submitted",
        save_dir=cfg.RESULTS_FOLDER,
        save_name="n_pints_map.png",
    )
    _, _ = gf.choropleth_map(
        shp,
        column="n_pubs",
        labels=True,
        cmap="YlGn",
        cmap_label="Number of Pubs",
        save_dir=cfg.RESULTS_FOLDER,
        save_name="n_pubs_map.png",
    )
    _, _ = gf.choropleth_map(
        shp,
        column="percentage_pubs_visited",
        labels=False,
        cmap="Purples",
        cmap_label="Percentage of Pubs Visited",
        save_dir=cfg.RESULTS_FOLDER,
        save_name="percentage_visited.png",
    )


if __name__ == "__main__":
    main()
