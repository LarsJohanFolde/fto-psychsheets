from dataclasses import dataclass
import sys
import requests
import pandas as pd

@dataclass
class Person:
    name: str
    average: float

    def time(self):
        minutes = int(self.average/60)
        seconds = round(self.average-minutes*60, 2)
        # I'm sorry you had to see this...
        return f"{str(minutes) + ":" if minutes else ""}{"%05.2f" % seconds}"

    def to_csv(self) -> str:
        average = self.time()
        return f'{self.name},{average}'

def get_competitors(competition_id: str) -> list[str]:
    url: str = f"https://worldcubeassociation.org/api/v0/competitions/{competition_id}/wcif/public"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error status: {response.status_code}")
        exit()

    data = response.json()
    competitors = []

    for person in data['persons']:
        # Splitting name to account for non-latin names
        name = person['name'].split(" (")[0]
        competitors.append(name)

    return competitors

def parse_csv(file: str) -> dict:
    data: pd.DataFrame = pd.read_csv(file)
    competitors: dict = {}
    names: list[str] = [name for name in data['name']]
    average: list[str] = [average.replace("\"", "") for average in data['average']]
    for i in range(len(names)):
        competitors.update({names[i]: average[i]})
    return competitors

def time_to_float(time: str) -> float:
    time = time.replace(",", ".")
    if ":" not in time:
        return float(time)
    split_time: list[str] = time.split(":")
    minutes: int = int(split_time[0])
    seconds: float = float(split_time[1])
    return seconds + minutes * 60

def data_to_csv(persons: list[list]) -> None:
    competition_id: str = sys.argv[1]
    output_file: str = f"./psychsheets/{competition_id}_psychsheet.csv"
    with open(output_file, 'w') as file:
        file.write("name,average\n")
        for person in persons:
            print(f"{person.name}: {person.time()}")
            file.write(f"{person.to_csv()}\n")
        print(f"\nData written to {output_file}")

def main() -> None:
    output: list[Person] = []
    competition_id: str = sys.argv[1]
    competitors: list[str] = get_competitors(competition_id)
    ranks: dict = parse_csv("fto_ranks.csv")

    for competitor in competitors:
        if competitor in ranks:
            person = Person(competitor, time_to_float(ranks[competitor]))
            output.append(person)

    output = sorted(output, key=lambda x: x.average)
    data_to_csv(output)

if __name__ == "__main__":
    main()
