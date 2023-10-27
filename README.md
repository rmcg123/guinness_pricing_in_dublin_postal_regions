## Geographic Variation of Guinness Pricing in Dublin (2017-18)

A small project to examine the geogrophic variation of Guinness pint pricing in
Dublin in the years 2017 and 2018.

The data is primarily sourced from the website [guindex](www.guindex.ie) using
their python package. This data is supplemented by data of Irish postal routing
areas which can be obtained from [here](https://autoaddress2.helpscoutdocs.com/article/129-routing-key-boundaries)
The file that I downloaded was `RoutingKeys_Shape_IG_2016_09_29.zip` 
(the ESRI Shapefile using Irish Grid Projection). This should be saved in the
folder `data/routing_keys/`.

The project uses a virtual environment running python `3.11`. The requirements
are listed in the `requirements.txt` file and can be installed by 
`pip install -r requirements.txt`.
