import logging as logger
from datetime import datetime
from oilanalytics.utils import chartutils as cu
from commodplot import jinjautils as ju
from pyenergyaspects import eaapi

fsu_stat_ids = [
    9042,
    9063,
    9092,
    10284,
    3956,
    3957,
    3958,
    3959,
    3960,
    4758,
    1294,
    8989,
    8991,
    3949,
    3952,
    3954,
    3955,
]


def generate_page(
    file_path: str = None,
    title_url: str = None,
):
    data = {
        "name": "FSU Stats",
        "title": "FSU Stats",
    }

    date_from = datetime(2010, 1, 1)

    data["df"] = eaapi.read_timeseries(dataset_id=fsu_stat_ids, date_from=date_from)

    data["title_url"] = title_url

    logger.info(f"generated page to {file_path}")
    return ju.render_html(
        data=data,
        template="fsu_stats.html",
        filename=file_path,
        package_loader_name="oilanalytics.energyaspects",
        template_globals={"cu": cu},
    )


if __name__ == "__main__":
    generate_page(file_path="fsu_stats.html")
