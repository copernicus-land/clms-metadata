import rioxarray
from cyclopts import App

app = App()


@app.default
def main(path_in: str, path_out: str) -> None:
    # min_x, min_y, max_x, max_y = 5.8175, 50.9216, 5.9343, 51.0857
    ds = rioxarray.open_rasterio(path_in)
    if ds.rio.crs is None:
        ds.rio.write_crs("EPSG:4326", inplace=True)
    ds = ds.rio.clip_box(ds.x[0], ds.y[0], ds.x[15], ds.y[15])
    ds.to_netcdf(path_out)


if __name__ == "__main__":
    app()
