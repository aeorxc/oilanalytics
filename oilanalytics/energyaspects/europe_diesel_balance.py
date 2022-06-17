import logging as logger
from datetime import datetime
from oilanalytics.utils import chartutils as cu
from commodplot import jinjautils as ju
from pyenergyaspects import eaapi

eur_diesel_ids = [11286, 11285, 11282, 11279, 11284, 11283, 11278, 11314, 11280, 11281]


def generate_page(
    file_path: str = None,
    title_url: str = None,
):
    data = {
        "name": "Europe Diesel Balance",
        "title": "Europe Diesel Balance",
    }

    date_from = datetime(2010, 1, 1)

    data["df"] = eaapi.read_timeseries(dataset_id=eur_diesel_ids, date_from=date_from)

    data["title_url"] = title_url

    logger.info(f"generated page to {file_path}")
    return ju.render_html(
        data=data,
        template="europe_diesel_balance.html",
        filename=file_path,
        package_loader_name="oilanalytics.energyaspects",
        template_globals={"cu": cu},
    )


if __name__ == "__main__":
    generate_page(file_path="europe_diesel_balance.html")
