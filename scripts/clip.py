import rioxarray
from cyclopts import App

app = App()


@app.default
def main(path_in: str, path_out: str) -> None:
    ds = rioxarray.open_rasterio(path_in)
    if ds.rio.crs is None:
        ds.rio.write_crs("EPSG:4326", inplace=True)
    x_min, x_max = sorted([ds.x[0], ds.x[15]])
    y_min, y_max = sorted([ds.y[0], ds.y[15]])
    ds = ds.rio.clip_box(x_min, y_min, x_max, y_max)
    ds.to_netcdf(path_out)


if __name__ == "__main__":
    app()
