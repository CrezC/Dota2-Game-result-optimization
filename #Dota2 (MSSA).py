#Dota2 (MSSA)
# Import necessary libraries
import pandas as pd
import json
import random
import matplotlib.pyplot as plt

# Load hero data from JSON file and return a dictionary mapping hero IDs to names
def load_hero_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        hero_id_to_name = {hero['id']: hero['localized_name'] for hero in data['heroes']}
        return hero_id_to_name

# Load match data from a CSV file
def load_data(file_path):
    return pd.read_csv(file_path)

# Calculate win rates for heroes based on match data
def calculate_hero_win_rates(data, hero_id_to_name):
    results = data.iloc[:, 0]  # Assume first column is match results
    hero_columns = data.columns[4:]  # Hero data starts from the 5th column
    hero_win_rates = {}
    for i, col in enumerate(hero_columns):
        if (i + 1) in hero_id_to_name:  # Check if hero ID is valid
            total_games = data[data[col] != 0].shape[0]
            win_games = data[(data[col] == 1) & (results == 1)].shape[0] + data[(data[col] == -1) & (results == -1)].shape[0]
            hero_win_rates[i + 1] = win_games / total_games if total_games > 0 else 0
    return hero_win_rates

# Multi-objective optimization using Salp Swarm Algorithm (simplified version)
def simple_mssa(valid_hero_ids, hero_win_rates, target_win_rate, num_heroes=5, iterations=50):
    population = [random.sample(valid_hero_ids, num_heroes) for _ in range(10)]
    best_solution = None
    best_fitness = float('inf')
    for _ in range(iterations):
        fitnesses = [1 / abs(sum(hero_win_rates.get(hero, 0) for hero in heroes) / len(heroes) - target_win_rate) for heroes in population]
        current_best_fitness = min(fitnesses)
        if current_best_fitness < best_fitness:
            best_fitness = current_best_fitness
            best_solution = population[fitnesses.index(best_fitness)]
        population = [random.sample(valid_hero_ids, num_heroes) for _ in population]
    return best_solution, best_fitness

# Visualize results as a bar chart
def visualize_results(data, title, ylabel):
    plt.figure(figsize=(10, 5))
    plt.bar(data.keys(), data.values(), color='blue')
    plt.xlabel('Hero')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()

# Get target win rate from user input
def get_target_win_rate():
    user_input = input("Please enter your desired win rate (e.g., 0.5 for 50%), 'random' for a random target, or 'no' for default: ")
    if user_input.lower() == 'random':
        return random.uniform(0.3, 0.7)  # Generate a random target win rate
    elif user_input.lower() == 'no':
        return 0.5  # Use default win rate if no input
    else:
        try:
            return float(user_input)
        except ValueError:
            return 0.5  # Default win rate if invalid input

# Filter heroes based on a win rate threshold
def filter_heroes_by_winrate(hero_win_rates, threshold=0.01):
    return {hero: rate for hero, rate in hero_win_rates.items() if rate > threshold}

# Main execution block
if __name__ == "__main__":
    hero_data_path = 'heroes.json'
    data_path = 'dota2Train.csv'
    hero_id_to_name = load_hero_data(hero_data_path)
    data = load_data(data_path)
    hero_win_rates = calculate_hero_win_rates(data, hero_id_to_name)
    filtered_hero_win_rates = filter_heroes_by_winrate(hero_win_rates, 0.01)
    valid_hero_ids = list(filtered_hero_win_rates.keys())
    target_win_rate = get_target_win_rate()  # Get target win rate from user
    best_solution, best_fitness = simple_mssa(valid_hero_ids, filtered_hero_win_rates, target_win_rate)
    best_solution_names = {hero_id_to_name[hero]: filtered_hero_win_rates.get(hero, 0) for hero in best_solution}
    print("Best Hero Combination:", best_solution_names, "with closeness to target win rate:", 1 / best_fitness)
    visualize_results(best_solution_names, "Hero Win Rates in Optimal Combination", "Win Rate")
