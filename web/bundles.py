from flask_assets import Environment, Bundle
from webassets.filter import get_filter

babel = get_filter('babel', presets='vue')

assets = {
    "main_js": Bundle(
        '../assets/yarn/vue-carousel/dist/vue-carousel.min.js',
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
    "bootstrap_css": Bundle(
        "../assets/yarn/bootstrap/dist/css/bootstrap.css",
        filters="cssmin",
        output="css/bootstrap.css"
    ),
    "bootstrap_js": Bundle(
        "../assets/yarn/bootstrap/dist/js/bootstrap.js",
        filters="jsmin",
        output="js/bootstrap.js"
    ),
    "jquery": Bundle(
        "../assets/yarn/jquery/dist/jquery.js",
        filters="jsmin",
        output="js/jquery.js"
    ),
    "slick_js": Bundle(
        "../assets/js/slick/slick.js",
        filters="jsmin",
        output="js/slick.js"
    ),
    "slick_css": Bundle(
        "../assets/js/slick/slick.scss",
        "../assets/js/slick/slick-theme.scss",
        filters="cssmin",
        output="css/slick.css"
    ),
}


def register_assets(assets_obj):
    for asset_name, asset in assets.items():
        assets_obj.register(asset_name, asset)