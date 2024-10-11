import cyclopts

import clms_metadata.cli.odata

app = cyclopts.App()
app.command(clms_metadata.cli.odata.app, name="odata")


if __name__ == "__main__":
    app()
