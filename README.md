## NBA Combine Draft Data

The NBA Combine is an annual event leading up to the NBA Draft, where prospective players are evaluated for their performance and playing ability. Invitees go through a series of athletic tests, drills, and interviews under observation from NBA coaches and management. They include physical anthropometric measurements, medical tests, athletic ability tests, and scrimmages. The NBA Combine helps NBA teams assess where the incoming talent pool is from a physical and mental perspective regarding readiness for professional basketball. It is a crucial step, among their previous playing career, in their journey to making it in the NBA.

### Functionality/Features

This script will grab NBA Combine Draft Data from the year 2000 to the current year.

It pulls data such as player_id, as a unique identifer, as well as their position, college/prior team, anthropometric data, and some athletic tests such as vertical jump, max bench press reps, and a few agility tests.

Beyond that, it has custom calculations to measure BMI (body mass index) and relative comparison scores for max bench press reps, three quarter sprint time, and max vertical leap. These scores are used to compare among the relative combine class for ease of analysis and reporting, and to highlight variations in player performances.

### Prerequisites
- Python 3.11.4 installed 
#### PostgreSQL
Before you begin, ensure that you have PostgreSQL installed on your computer. If you don't have PostgreSQL installed, follow the installation instructions below based on your operating system.
- Windows

	1.	Download the installer from the official PostgreSQL website.
	2.	Run the downloaded file and follow the installation wizard instructions.
- macOS
	1.	Install Homebrew (if not already installed) by running:
`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  2.	Install PostgreSQL using Homebrew: `brew install postgresql`

#### Start Postgres Service:
- Windows: Use the Services application to start the PostgreSQL service.
- macOS: `brew services start postgresql`


### Installation
1. Clone the repository

```commandline
git clone https://github.com/markprubin/nba-combine.git
cd nba-combine
```
2. Set up a virtual environment (optional, but recommended):
```commandline
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

```
3. Install the dependencies:
```commandline
pip install -r requirements.txt

```

### Usage

#### Create the Database
Go to your terminal and type in:
```commandline 
psql
```
Type in:
```commandline 
CREATE DATABASE nba_combine;
- ```
Then, if you do not have a username and password, enter:
```commandline
CREATE USER yourusername WITH ENCRYPTED PASSWORD 'yourpassword';
```
replacing *yourusername* and *yourpassword* with your choice.

Finish with the following, replacing with your username and password
```commandline
GRANT ALL PRIVILEGES ON DATABASE nba_combine TO yourusername;
```

Then exit with `\q`

Create a .env file, and put in the file the following: `DB_URL=postgresql://yourusername:yourpassword@localhost/nba_combine`, again, replacing the username and password fields with your own that you set up.

#### Initialize the Database
- Ensure that RESET_DB = True in the init_db.py file before you run the main script.

#### Run the script

- Navigate to the main directory of the project.

Execute:
`python3 main.py`

- This will initialize your database and run the script to load the data.

- NOTE: If you want to reset the database (drop and create the database from scratch), go to init_db.py and set RESET_DB = True and run the script. This is located in "nba-combine/init_db.py".

### Dependencies

- certifi==2023.11.17
- charset-normalizer==3.3.2
- idna==3.7
- nba_api==1.4.1
- numpy==1.26.4
- pandas==2.2.2
- psycopg2==2.9.9
- python-dateutil==2.9.0.post0
- python-dotenv==1.0.1
- pytz==2024.1
- requests==2.32.2
- scipy==1.13.1
- six==1.16.0
- SQLAlchemy==2.0.30
- typing_extensions==4.11.0
- tzdata==2024.1
- urllib3==2.2.1


### Challenges:

1. The output was not being recognized as a dictionary, but as an entire string:

`ERROR:root:Error processing data: string indices must be integers, not 'str'`

Therefore, I realized that the type was of class<str>, and I had to adjust fetching the data into json.loads(data) to set it as a dictionary.

2. Confirmed that 'Shuttle Run' is listed as Modified Lane Agility Time on the api through https://www.nba.com/stats/draft/combine-strength-agility?SeasonYear=2019-20 and matching the values.
3. Had an issue with the BMI calculation getting rid of around half of the players in a specific year based on my initial logic on the if statement, where I said if they were greater than 0, proceed. I changed it height and weight "is not None", and it gave me all the players, even if no height or weight was recorded.
4. Ran into multiple session rollbacks when updating the database with the range of annual data. Any repeated player_id's due to prior attendance created an error and cause the data for that year not to upload. Therefore, I set the primary key in my model to player_id AND season_year, allowing for multiple appearances of players.
5. I had fetched the college's attended for each player within the loop of fetching each year's data, which is overly taxing on the API. I created a static method to retrieve the data once and call before the loop, using it as a temporary storage, as the college data is not attached to a specific year.
6. Adjusted processing weight data to recognize empty strings. I wanted to treat any empty occurrences as null to correctly calculate bmi. I will definitely adjust the original intake of weight as a float instead to reduce any conditionals needed in case of str/float errors.
### Adjustments to prompt:

I have added the following columns for easier referencing and data availability if needed, as I felt player_id was not sufficient:
- First name *(Quick referencing)*
- Last name *(Quick referencing)*
- Position *(Helpful for grouping data by position)*
- Season-Year *(For year referencing)*



### Future Considerations
- **Database Creation**: I plan on creating a .sh file that will create the database automatically.
- **Robust Testing**: I would implement Pytest to ensure proper testing for each part of the data retrieval and processing the data.
- **Data Visualization**: Implement functionality for visualizing data trends over the years, such as changes in player measurements or performance scores. Potentially compare to success within the NBA, if drafted.
- **Expanded Data Sources**: Consider integrating additional data sources to enrich the dataset with more detailed player profiles or historical performance metrics.
- **Machine Learning**: ML models can be explored to predict player success based on combine data, which could be a valuable tool for scouting.