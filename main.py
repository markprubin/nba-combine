from nba_api.stats.endpoints import draftcombinestats, drafthistory, draftboard

from sqlalchemy.orm import sessionmaker
from init_db import engine
from models.models import Player

import numpy as np
from scipy.stats import zscore

import logging
import json
from datetime import datetime


# Basic logging set up
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

Session = sessionmaker(bind=engine)


class NBADraftCombineDataHandler:

    def __init__(self, season_all_time, league_id='00'):
        self.league_id = league_id
        self.season_all_time = season_all_time

    def fetch_data(self, college_data):
        """
        Fetches player data and combines it with college data.

        :param college_data: The college data to combine with player data.
        :type college_data: dict

        :return: The combined player and college data as a dictionary.
        """

        try:
            # Fetch Player anthropometric data and stats. Load as json, as get_json() loads it as a string.
            player_data = draftcombinestats.DraftCombineStats(league_id=self.league_id, season_all_time=self.season_all_time)
            player_json = player_data.get_json()
            player_data = json.loads(player_json)

            combined_data = {
                "player_data": player_data,
                "college_data": college_data
            }

            logging.info("Data fetched successfully")

            return combined_data

        except Exception as e:
            logging.error(f'Error fetching NBA Draft Combine data: {e}')
            return None

    # Fetch and store college data
    @staticmethod
    def fetch_college_data():
        """
        A static method that fetches college data from draft history.

        :return: A dictionary containing college data.
        """

        draft_history = drafthistory.DraftHistory()
        draft_data = draft_history.draft_history.get_dict()['data']
        college_data = {item[0]: item[11] for item in
                        draft_data}
        return college_data

    def process_data(self, raw_data: dict) -> list:
        """
        Process raw data to generate a list of processed players.

        :param raw_data: Dictionary containing raw player data.
        :return: List of processed Player objects.
        """
        processed_players = []
        college_data = raw_data['college_data']
        # Season year had to be assigned as the string in a different area of raw_data to be able to access it for the score portion, as the other data was just returning the first year
        season_year = raw_data['player_data']['parameters']['SeasonYear']
        try:
            for player_data in raw_data['player_data']['resultSets'][0]['rowSet']:
                player = Player()
                player.player_id = player_data[1]
                player.first_name = player_data[2]
                player.last_name = player_data[3]
                player.position = player_data[5] if player_data[5] else "Not Available"
                player.season_year = season_year
                player.team = college_data.get(player.player_id, None)
                player.height = player_data[6] if player_data[6] is not None else None
                player.weight = player_data[10] if player_data[10] not in (None, '') else None
                player.wingspan = player_data[11] if player_data[11] is not None else None
                player.standing_reach = player_data[13] if player_data[13] is not None else None
                player.standing_vertical_leap = player_data[18] if player_data[18] is not None else None
                player.lane_agility_time = player_data[20] if player_data[20] is not None else None
                player.shuttle_run_time = player_data[21] if player_data[21] is not None else None
                player.three_quarter_sprint_time = player_data[22] if player_data[22] is not None else None
                player.max_vertical_leap = player_data[19] if player_data[19] is not None else None
                player.max_bench_press_reps = player_data[23] if player_data[23] is not None else None

                #BMI
                if player.height is not None and player.weight is not None:
                    player.bmi = round(self.calculate_bmi(player.height, player.weight), 1)
                else:
                    player.bmi = None
                processed_players.append(player)
            logging.info("Data processed successfully")
        except Exception as e:
            logging.error(f'Error processing data: {e}')
        return processed_players

    @staticmethod
    def store_data(session, processed_players):
        try:
            session.add_all(processed_players)
            session.commit()
            logging.info("Data stored successfully")
        except Exception as e:
            session.rollback()
            logging.error(f"Error storing data: {e}")

    @staticmethod
    def calculate_bmi(height: float, weight: str) -> float:
        """
        Calculate BMI based on given height and weight.

        :param height: The height of the person in inches.
        :param weight: The weight of the person in pounds.
        :return: The calculated BMI value.
        """

        bmi = (float(weight) / (float(height) ** 2)) * 703
        return bmi

    def calc_and_store_scores(self, session, *metrics):
        """
        :param session: Session object for query and commit to the database.
        :param metrics: Variable number of metrics as strings for which scores will be calculated and stored.

        :return: None

        This method calculates and stores scores for each player in the database based on the provided metrics. It uses the z-score transformation to standardize the metric data and assigns
        * a score to each player based on the z-score.

        Example usage:
            session = create_session()  # Creates a session object
            calc_and_store_scores(session, 'max_bench_press_reps', 'max_vertical_leap')  # Calculate and store scores for 'bench press reps' and 'maximum vertical leap' metrics

        """
        # Query all the players for the given season year
        players = session.query(Player).filter_by(season_year=self.season_all_time).all()

        if not players:
            logging.error("No players found for the season.")
            return

        # Analyze each metric within the multiple metrics put in the function. Returns
        for metric in metrics:
            metric_data = [getattr(player, metric) for player in players if getattr(player, metric) is not None]

            if not metric_data:
                logging.warning(f"No valid data found for metric: {metric}")
                continue

            # Assigned the metric data in a list as a Numpy Array to calculate z-scores
            np_metric_data = np.array(metric_data, dtype=float)
            z_scores = zscore(np_metric_data)

            # Go through z-scores and assign to each respective player
            index = 0
            for player in players:
                if getattr(player, metric) is not None:
                    score = 100 + 15 * z_scores[index]
                    setattr(player, metric + '_score', score)
                    # Increment if player has metric
                    index += 1

        try:
            session.commit()
            logging.info("Scores calculated and stored successfully.")
        except Exception as e:
            session.rollback()
            logging.error(f"Failed to store scores: {e}")


def main():

    # Start year associated with NBA Draft Combine API data availability.
    start_year = 2000
    current_year = datetime.now().year

    # College data fetched once outside the loop.
    college_data = NBADraftCombineDataHandler.fetch_college_data()

    # Starts the process of gathering data in a range of the start year to the current year for reuse.
    for year in range(start_year, current_year):
        # The season_all_time parameter is based off a format of "20xx-xx", so slicing the last two digits
        season_all_time = f"{year}-{str(year+1)[2:]}"
        data_handler = NBADraftCombineDataHandler(season_all_time)
        raw_data = data_handler.fetch_data(college_data)
        if raw_data:
            processed_data = data_handler.process_data(raw_data)
            if processed_data:
                session = Session()
                try:
                    data_handler.store_data(session, processed_data)
                    data_handler.calc_and_store_scores(session,
                                                       'three_quarter_sprint_time',
                                                       'max_vertical_leap',
                                                       'max_bench_press_reps')
                    session.close()
                except Exception as e:
                    session.rollback()
                    logging.error(f"Failed during database operations: {e}")
                finally:
                    session.close()
            else:
                logging.warning("No data processed")
        else:
            logging.warning('Failed to fetch data.')


if __name__ == '__main__':
    main()
