from nba_api.stats.endpoints import draftcombineplayeranthro, draftcombinestats
import numpy as np
from sqlalchemy.orm import sessionmaker
from init_db import engine
from models.models import Player
import logging
import json


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

Session = sessionmaker(bind=engine)


class NBADraftCombineDataHandler:

    def __init__(self, season_all_time, league_id='00'):
        self.league_id = league_id
        self.season_all_time = season_all_time

    def fetch_data(self):
        """
        Fetches data from the nba_api library from multiple endpoints.
        :return: A list of player anthropometric data in the respective year for the NBA.
        """

        try:
            player_data = draftcombinestats.DraftCombineStats(league_id=self.league_id, season_all_time=self.season_all_time)
            data = player_data.get_json()
            data = json.loads(data)
            logging.info("Data fetched successfully")
            return data

        except Exception as e:
            logging.error(f'Error fetching NBA Draft Combine data: {e}')
            return None

    def process_data(self, raw_data):
        processed_players = []
        try:
            for player_data in raw_data['resultSets'][0]['rowSet']:
                player = Player()
                player.player_id = player_data[1]
                player.first_name = player_data[2]
                player.last_name = player_data[3]
                player.position = player_data[5]
                player.team = "Default Team"
                player.height = player_data[6] if player_data[6] is not None else 0.0
                player.weight = player_data[10] if player_data[10] is not None else "unknown"
                player.wingspan = player_data[11] if player_data[11] is not None else 0.0
                player.standing_reach = player_data[13] if player_data[13] is not None else 0.0
                player.vertical_leap = player_data[19] if player_data[19] is not None else 0.0
                player.bench_press_reps = player_data[23] if player_data[23] is not None else 0
                player.lane_agility_time = player_data[20] if player_data[20] is not None else 0.0
                player.shuttle_run_time = player_data[21] if player_data[21] is not None else 0.0
                # Placeholders for calculations to come
                player.three_quarter_sprint_time_score = None
                player.max_vertical_leap_score = None
                player.max_vertical_leap_time_score = None

                #BMI
                if player.height and float(player.weight) > 0:
                    player.bmi = round(self.calculate_bmi(player.height, float(player.weight)), 1)
                else:
                    player.bmi = None
                processed_players.append(player)
            logging.info("Data processed successfully")
        except Exception as e:
            logging.error(f'Error processing data: {e}')
        return processed_players

    def store_data(self, processed_players):
        session = Session()
        try:
            session.add_all(processed_players)
            session.commit()
            logging.info("Data stored successfully")
        except Exception as e:
            session.rollback()
            logging.error(f"Error storing data: {e}")
        finally:
            session.close()

    def calculate_bmi(self, height, weight):
        bmi = (weight / (height ** 2)) * 703
        return bmi

    # def calculate_scores(self, data):
    #


def main():
    data_handler = NBADraftCombineDataHandler(season_all_time='2019-20')
    raw_data = data_handler.fetch_data()
    print(raw_data)
    if raw_data:
        processed_data = data_handler.process_data(raw_data)
        if processed_data:
            data_handler.store_data(processed_data)
        else:
            logging.warning("No data processed")
    else:
        logging.warning('Failed to fetch data.')


if __name__ == '__main__':
    main()