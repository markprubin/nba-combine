Challenges:

The output was not being recognized as a dictinary, but as an entire string.

ERROR:root:Error processing data: string indices must be integers, not 'str'

Therefore, I realized that the type was of class<str>, and I had to adjust fetching the data into json.loads(data) to put it as a dictionary.

Confirmed that 'Shuttle Run' is listed as Modified Lane Agility Time on the api through https://www.nba.com/stats/draft/combine-strength-agility?SeasonYear=2019-20 and matching the values.