import cyclopts

import clms_metadata.cli.odata
import clms_metadata.cli.product

app = cyclopts.App()
app.command(clms_metadata.cli.odata.app, name="odata")
app.command(clms_metadata.cli.product.app, name="product")


def main():
    app()


if __name__ == "__main__":
    main()
