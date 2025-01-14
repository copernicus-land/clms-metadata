import rioxarray
from cyclopts import App

app = App()


@app.default
def main(path_in: str, path_out: str) -> None:
    min_x, min_y, max_x, max_y = 58.8175, 13.9216, 58.9343, 14.0857
    ds = rioxarray.open_rasterio(path_in)
    ds = ds.rio.clip_box(min_x, min_y, max_x, max_y)
    ds.to_netcdf(path_out)


if __name__ == "__main__":
    app()
