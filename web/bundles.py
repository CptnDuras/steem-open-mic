from flask_assets import Environment, Bundle
from webassets.filter import get_filter

babel = get_filter('babel', presets='vue')

assets = {
    "main_js": Bundle(
        '../assets/js/main.js',
        filters=babel,
        output="js/main.js"
    ),
    # "steem_js": Bundle(
    #     '../assets/js/sc2.min.js',
    #     '../assets/js/steem.min.js',
    #     filters=babel,
    #     output="js/steem.js"
    # ),
}


def register_assets(assets_obj):
    for asset_name, asset in assets.items():
        assets_obj.register(asset_name, asset)