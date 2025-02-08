import sys
sys.path.append("./logic_puzzle/")

import pickle
from tqdm import tqdm
from z3 import *
import json
import argparse
import solver as solver
import check_clues
import graph_literals
from collections import defaultdict
import sat_utils
import multiprocessing
from functools import partial
from tqdm.auto import tqdm


def get_idx2clue(clues):
    clue_num2_clue = defaultdict(int)
    clue_type2_clue_num = defaultdict(list)
    clue_num = 0
    for clue in list(clues):
        clue_num2_clue[clue_num] = clue
        clue_type2_clue_num[type(clue)].append(clue_num)
        clue_num += 1
    return clue_num2_clue, clue_type2_clue_num

def solve_single_puzzle(args):
    """Process a single puzzle and return its reasoning result"""
    try:
        puzzle_data, answers_data = args
        
        d = puzzle_data
        
        # Removed print statements that would clutter multiprocessing output
        answer_header = answers_data['solution']['table_header']
        answer_value = answers_data['solution']['table_rows']
        
        puzzle_clues = d['puzzle'].clues
        idx2clue, clue_type2_idx = get_idx2clue(puzzle_clues)
        
        running_clues = []
        all_cells = []
        used_clue = []
        self_constraints = d['puzzle'].constraints
        running_clues.extend(self_constraints)
        
        first = True
        step_num = 1
        reasoning = ""
        
        while len(used_clue) < len(idx2clue):
            reasoning += f'Step {step_num}: '
            step_num += 1
            clue_idxs = check_clues.check(d['idx'],
                                        answer_header, answer_value,
                                        running_clues, idx2clue, used_clue, all_cells)
            for current_clue_idx in clue_idxs:
                running_clues.extend(idx2clue[current_clue_idx].as_cnf())
                used_clue.append(current_clue_idx)

            numbered_cnf, num2var = sat_utils.translate(running_clues)
            single_solver = solver.my_solver(d['idx'], answer_header, answer_value, numbered_cnf, num2var)
            cell_info = single_solver.check_cell_difficulty()
            new_cell = []
            for cell in cell_info:
                if cell not in all_cells:
                    new_cell.append(cell)
                    all_cells.append(cell)
            reasoning += graph_literals.print_clue(clue_idxs, idx2clue, new_cell, first)
            first = False
            reasoning += '\n'
        
        reasoning += 'The puzzle is solved.'
        
        single_data = answers_data.copy()
        single_data["reasoning"] = reasoning
        return single_data
    except Exception as e:
        print(f"Failed to process puzzle {puzzle_data['idx']}: {str(e)}")
        return None

def logic_grid_puzzle(inputfile, ground_truth, size, lower_part, higher_part):
    answers = json.load(open(ground_truth, 'r'))
    puzzles = pickle.load(open(inputfile, 'rb'))
    mode = inputfile[inputfile.find('puzzles.') + 8:inputfile.find('.pkl')]
    print('Number of puzzles:', len(answers))
    assert len(answers) == len(puzzles)
    
    # Filter puzzles based on size and range
    filtered_puzzles = []
    filtered_answers = []
    for i, (puzzle, answer) in enumerate(zip(puzzles, answers)):
        per_size_idx = int(puzzle['idx'].split('-')[-1])
        if (puzzle['idx'].startswith(f"lgp-{mode}-{size}") and 
            lower_part <= per_size_idx < higher_part):
            filtered_puzzles.append(puzzle)
            filtered_answers.append(answer)
    
    print(f'Processing {len(filtered_puzzles)} puzzles using {multiprocessing.cpu_count()} CPU cores')
    
    # Set up multiprocessing with progress bar
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    
    # Create pairs of puzzle and answer data only
    puzzle_pairs = list(zip(filtered_puzzles, filtered_answers))
    
    # Process puzzles in parallel with progress bar
    raw_results = list(tqdm(
        pool.imap(solve_single_puzzle, puzzle_pairs),
        total=len(filtered_puzzles),
        desc="Solving puzzles"
    ))
    
    # Filter out None results from failed puzzles
    results = [r for r in raw_results if r is not None]
    
    print(f'Successfully processed {len(results)} out of {len(filtered_puzzles)} puzzles')
    
    pool.close()
    pool.join()
    
    # Save results
    output_path = f"./data/logic_grid_puzzles.reasoning.{mode}{size}-{lower_part}_{higher_part}.json"
    print(f'\nSaving results to {output_path}')
    with open(output_path, "w") as outputfile:
        json.dump(results, outputfile)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_data', type=str, default="./data/logic_grid_puzzles.test_id_xl.pkl")
    parser.add_argument('--ground_truth', type=str, default="./data/ogic_grid_puzzles.test_id_xl.json")
    parser.add_argument('--size', type=str, default="2x")
    parser.add_argument('--lower_part', type=int, default=0) #min data index
    parser.add_argument('--higher_part', type=int, default=999999999) #max data index
    args = parser.parse_args()

    logic_grid_puzzle(args.input_data, args.ground_truth, args.size, args.lower_part, args.higher_part)
    return 1

if __name__ == "__main__":
    main()
