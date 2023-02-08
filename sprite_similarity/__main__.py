import argparse
import logging
import sys

from pathlib import Path

from sprite_similarity.utils import setup_logger
from sprite_similarity.io import load_snapshot, crawl_assets, save_results, create_figures
from sprite_similarity.preprocess import preprocess
from sprite_similarity.compare_pixels import get_mean_squared_errors

def main(path_snapshot, path_results, bg_color, enable_figures, quiet):
    # set up logging interface
    logger_name = path_snapshot.name
    path_logs = Path("./log")
    logger = setup_logger(path_logs, logger_name=logger_name, quiet=quiet)
    
    # if not enable_logging:
    #     logging.disable(level="CRITICAL")
        
    logger.info(f"Starting visual analysis for snapshot '{path_snapshot}', writing results to '{path_results}'")
    
    # load the input data
    ss, df = load_snapshot(path_snapshot, logger_name=logger_name)

    # crawl urls of game textures used in scene
    crawl_assets(df, logger_name=logger_name) # TODO should do this at same time as collecting snapshot
    
    # preprocess 
    asset_oracles, obj_images = preprocess(ss, df, bg_color, cw=False, logger_name=logger_name)
    
    # calculate the errors between generated oracles and rendered objects
    errors = get_mean_squared_errors(asset_oracles, obj_images)
    
    # save the results to csv
    save_results(errors, path_results, path_snapshot.name)
    
    # optionally save the results summary image
    if enable_figures:
        create_figures(asset_oracles, obj_images, errors, path_results, path_snapshot.name)
    
    logger.info(f"Finished visual analysis for '{path_snapshot}', wrote results to '{path_results}'")


if __name__ == "__main__":
    # set up command-line argument parser
    parser = argparse.ArgumentParser(
                    prog = 'python3 analyse.py',
                    description = 'Visually analyse data collected from a PIXI application',
                    epilog = "For more help, visit: https://github.com/asgaardlab/canvas-visual-bugs-testbed")
    parser.add_argument("path_snapshot", type=Path)
    parser.add_argument("-o", "--path_results", type=Path, default=Path("./results"))
    parser.add_argument("-c", "--background_color", type=tuple, default=(0, 0, 0, 255))
    parser.add_argument("-f", "--enable_figures", action='store_false')
    parser.add_argument("-q", "--quiet", action='store_true')
    
    # read the arguments
    args = parser.parse_args()
    
    # run the script
    main(
        args.path_snapshot, 
        args.path_results, 
        args.background_color,
        args.enable_figures,
        args.quiet,
    )
