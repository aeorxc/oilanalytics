import logging as logger
from datetime import datetime

from commodplot import jinjautils as ju
from pyenergyaspects import eaapi

from oilanalytics.utils import chartutils as cu

china_stat_ids = [
    3333,
    3334,
    3335,
    3336,
    3337,
    3325,
    3326,
    3329,
    3338,
    3339,
    3340,
    3341,
    3342,
    3343,
    3344,
    3345,
    3346,
    3347,
    3348,
    3349,
    3350,
    3351,
    3352,
    3330,
    3358,
    3359,
    3360,
    3361,
    3362,
    3363,
    3364,
    3365,
    3366,
    3367,
    3368,
    3369,
    3331,
    3332,
    1446,
    1481,
    1479,
    1480,
    3324,
]


def generate_page(
    file_path: str = None,
    title_url: str = None,
):
    data = {
        "name": "China Stats",
        "title": "China Stats",
    }

    date_from = datetime(2010, 1, 1)

    data["df"] = eaapi.read_timeseries(dataset_id=china_stat_ids, date_from=date_from)

    data["title_url"] = title_url

    logger.info(f"generated page to {file_path}")
    return ju.render_html(
        data=data,
        template="china_stats.html",
        filename=file_path,
        package_loader_name="oilanalytics.energyaspects",
        template_globals={"cu": cu},
    )


if __name__ == "__main__":
    generate_page(file_path="china_stats.html")
