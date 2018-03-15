from flask_assets import Environment, Bundle
from webassets.filter import get_filter

babel = get_filter('babel', presets='vue')

assets = {
    "main_js": Bundle(
        '../assets/js/home.js',
        '../assets/js/main.js',
        filters=babel,
        output="js/main.js"
    ),
    "som_css": Bundle(
        "../assets/css/som.css",
        filters="cssmin",
        output="css/som.css"
    ),
    "fontawesome": Bundle(
        "../assets/yarn/font-awesome/css/font-awesome.css",
        filters="cssmin",
        output="css/fa.css"
    ),
    "bulma": Bundle(
        "../assets/yarn/bulma/css/bulma.css",
        filters="cssmin",
        output="css/bulma.css"
    ),
}


def register_assets(assets_obj):
    for asset_name, asset in assets.items():
        assets_obj.register(asset_name, asset)